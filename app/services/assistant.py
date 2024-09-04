from openai import OpenAI
from config import Config
import time
from flask import current_app
import json

class AssistantService:
    def __init__(self):
        self.openAI = OpenAI(api_key=Config.OPENAI_KEY)
        self.assistant_id = Config.ASSISTANT_ID
        self.assistant = self.get_assistant()
        self.thread = self.get_or_create_thread()

    def get_assistant(self):
        try:
            return self.openAI.beta.assistants.retrieve(self.assistant_id)
        except Exception as e:
            current_app.logger.error(f"Error retrieving assistant: {e}")
            return None

    def get_or_create_thread(self):
        try:
            if 'thread_id' in current_app.config:
                current_app.logger.info('Getting thread')
                return self.openAI.beta.threads.retrieve(current_app.config['thread_id'])
            else:
                current_app.logger.info('Creating thread')
                thread = self.create_thread()
                current_app.config['thread_id'] = thread.id
                return thread
        except Exception as e:
            current_app.logger.error(f"Error in get_or_create_thread: {e}")
            return None

    def create_thread(self):
        current_app.logger.info('Creating thread')
        try:
            return self.openAI.beta.threads.create()
        except Exception as e:
            current_app.logger.error(f"Error creating thread: {e}")
            return None

    def add_message_to_thread(self, role, message):
        current_app.logger.info(f'Adding message to thread: {role}, {message}')
        try:
            return self.openAI.beta.threads.messages.create(
                thread_id=self.thread.id,
                role=role,
                content=message,
            )
        except Exception as e:
            current_app.logger.error(f"Error adding message to thread: {e}")
            return None

    def run_assistant(self, message):
        current_app.logger.info(f'Running assistant: {message}')
        message = self.add_message_to_thread("user", message)
        if not message:
            return "Failed to add message to thread"

        try:
            run = self.openAI.beta.threads.runs.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
            )
            run = self.wait_for_update(run)

            if run.status == "failed":
                current_app.logger.info('Run failed')
                return "Assistant run failed"
            elif run.status == "requires_action":
                current_app.logger.info(f'Run requires action: {run}')
                return self.handle_require_action(run)
            else:
                current_app.logger.info('Run completed')
                return self.get_last_assistant_message()
        except Exception as e:
            current_app.logger.error(f"Error in run_assistant: {e}")
            return "Error occurred while running assistant"

    def handle_require_action(self, run):
        current_app.logger.info('Handling required action')
        try:
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            current_app.logger.info(tool_calls)
            tool_outputs = self.generate_tool_outputs(tool_calls)

            run = self.openAI.beta.threads.runs.submit_tool_outputs(
                thread_id=self.thread.id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )
            
            run = self.wait_for_update(run)

            if run.status == "failed":
                current_app.logger.info('Run failed')
                return "Action handling failed"
            elif run.status == "completed":
                return self.get_last_assistant_message()
            else:
                return "Unexpected status after action handling"
        except Exception as e:
            current_app.logger.error(f"Error in handle_require_action: {e}")
            return "Error occurred while handling required action"

    def wait_for_update(self, run):
        while run.status == "queued" or run.status == "in_progress":
            time.sleep(1)
            run = self.openAI.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=run.id,
            )
            current_app.logger.info(run.status)
        return run

    def get_last_assistant_message(self):
        current_app.logger.info('Getting last assistant message')
        try:
            messages = self.openAI.beta.threads.messages.list(thread_id=self.thread.id)
            if messages.data and messages.data[0].role == 'assistant':
                message = messages.data[0]
                for content_block in message.content:
                    if content_block.type == 'text':
                        return content_block.text.value
            return "No assistant message found"
        except Exception as e:
            current_app.logger.error(f"Error getting last assistant message: {e}")
            return "Error retrieving assistant message"

    def generate_tool_outputs(self, tool_calls):
        current_app.logger.info('Generating tool outputs')
        tool_outputs = []

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            arguments = tool_call.function.arguments
            tool_call_id = tool_call.id

            try:
                args_dict = json.loads(arguments)

                if hasattr(self, function_name):
                    function_to_call = getattr(self, function_name)
                    output = function_to_call(**args_dict) 

                    tool_outputs.append({
                        "tool_call_id": tool_call_id,
                        "output": output,
                    })
                else:
                    current_app.logger.warning(f"Function {function_name} not found")
            except json.JSONDecodeError:
                current_app.logger.error(f"Invalid JSON in arguments: {arguments}")
            except Exception as e:
                current_app.logger.error(f"Error in generate_tool_outputs: {e}")

        return tool_outputs

    # Les méthodes define_function_*, getUserIdByUsername, getPermissionsByUsername, 
    # et updateUserPermission restent inchangées
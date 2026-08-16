from pathlib import Path
import re


class PromptBuilder:
    """
    Builds prompts by combining the system prompt with
    a task-specific prompt template.
    """

    def __init__(self, prompt_directory="prompts"):
        self.prompt_directory = Path(prompt_directory)

    def load_prompt(self, filename):
        """
        Load a prompt template from the prompts directory.
        """
        file_path = self.prompt_directory / filename

        if not file_path.exists():
            raise FileNotFoundError(f"Prompt file '{filename}' not found.")

        return file_path.read_text(encoding="utf-8")

    def fill_template(self, template, **kwargs):
        """
        Replace only placeholders like:
        {input_text}
        {persona}
        {creativity_level}

        Leave normal JSON unchanged.
        """
        pattern = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")

        def replace(match):
            key = match.group(1)
            return str(kwargs.get(key, match.group(0)))

        return pattern.sub(replace, template)

    def build_prompt(self, task, **kwargs):
        """
        Build the final prompt.
        """

        system_prompt = self.load_prompt("system_prompt.md")
        task_prompt = self.load_prompt(f"{task}.md")

        task_prompt = self.fill_template(task_prompt, **kwargs)

        return f"""{system_prompt}

----------------------------------------

{task_prompt}
"""
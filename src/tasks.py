from crewai import Task

class BookTasks:
    def generate_outline(self, agent, title, description):
        return Task(
            description=(
                f"Create a detailed 15-20 chapter outline for a book titled '{title}'. \n"
                f"Theme/Description: {description}\n\n"
                "The outline must follow this exact format for each chapter:\n"
                "### Chapter N: Title\n"
                "* **The Hook**: A brief, engaging 'Head First' style hook.\n"
                "* **Topics**:\n"
                "    * Topic 1\n"
                "    * Topic 2\n\n"
                "Ensure the chapters progress logically from foundations to advanced topics."
            ),
            expected_output="A full 18-chapter Markdown outline.",
            agent=agent
        )

    def expand_syllabus(self, agent, chapter_title, chapter_topics):
        return Task(
            description=(
                f"Analyze the chapter: '{chapter_title}' and its topics: '{chapter_topics}'. "
                "Your goal is to expand this into a detailed, granular outline of at least 10-15 distinct sub-sections. "
                "Each sub-section will be the basis for a 300-400 word section of the book. "
                "Think about 'Head First' style: specific concepts, analogies, examples, and 'aha!' moments. "
                "Return the output as a Python list of strings, where each string is a sub-section title with a brief description."
            ),
            expected_output="A Python list of strings, e.g., ['Sub-section 1: Description...', 'Sub-section 2: Description...']",
            agent=agent
        )

    def write_section(self, agent, section_title, section_description, style_guide):
        return Task(
            description=(
                f"Write a comprehensive, engaging section for the topic: '{section_title}'. "
                f"Context: {section_description}. "
                f"Follow this Style Guide strictly:\n{style_guide}\n"
                "The section must be AT LEAST 300 words. "
                "Use analogies, 'we'/'you' language, and humor. "
                "Include a placeholder for a diagram if a concept is complex. "
                "Do NOT write a conclusion or summary at the end unless it's the very last section of the chapter."
            ),
            expected_output="A 300-400 word Markdown formatted text.",
            agent=agent
        )

    def review_content(self, agent, context):
        return Task(
            description=(
                "Review the draft content provided in the context for technical accuracy and 'Head First' style adherence. "
                "Check for:\n"
                "1. Is the analogy clear and accurate?\n"
                "2. Is the tone conversational enough?\n"
                "3. Are there any hallucinations?\n"
                "4. Is the length sufficient?\n"
                "Provide specific, actionable feedback. If it's good, just say 'Approved'."
            ),
            expected_output="A short paragraph of feedback or 'Approved'.",
            agent=agent,
            context=context
        )

    def edit_content(self, agent, context):
        return Task(
            description=(
                "Finalize the content. Use the original draft and the reviewer feedback provided in the context. "
                "If the feedback is 'Approved', simply return the original content formatted perfectly. "
                "If there is feedback, rewrite the necessary parts to address it. "
                "Ensure the final output is pure Markdown with no preamble."
            ),
            expected_output="Final, polished Markdown content.",
            agent=agent,
            context=context
        )

    def format_chapter(self, agent, content):
        return Task(
            description=(
                "You are provided with the full content of a chapter. Your task is to apply "
                "consistent formatting and stylistic normalization across the entire text. \n\n"
                "Rules:\n"
                "1. Chapter Title must be # H1. IMPORTANT: Remove any leading numbers like 'Chapter 1: ' or '1. '. The title should just be the text.\n"
                "2. Major Sections must be ## H2. Remove any leading numbers like 'Section 1.1' or '1. '.\n"
                "3. Sub-sections must be ### H3. Again, remove any numbering in the text of the header.\n"
                "4. All code blocks must specify a language (e.g., ```python).\n"
                "5. Ensure consistent spacing between paragraphs and headers.\n"
                "6. Standardize the appearance of 'Head First' elements like 'There Are No Dumb Questions' or 'Geek Bits'.\n\n"
                f"Chapter Content:\n{content}"
            ),
            expected_output="The exact same content but with perfectly consistent Markdown formatting and no numbering in titles.",
            agent=agent
        )

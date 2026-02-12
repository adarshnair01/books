from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
import os

class BookAgents:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            verbose=True,
            temperature=0.7,
            google_api_key=os.getenv("GEMINI_API_KEY")
        )

    def content_strategist(self):
        return Agent(
            role='Content Strategist',
            goal='Expand high-level chapter topics into detailed, actionable sub-sections to ensure a comprehensive 400-page book.',
            backstory=(
                "You are a master curriculum designer and book architect. "
                "You understand that to write a long, detailed book from a short outline, "
                "you must break down every topic into granular sub-concepts, examples, and deep dives. "
                "Your job is to take a single chapter topic and explode it into 10-20 distinct sub-sections "
                "that a writer can then flesh out."
            ),
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def writer(self):
        return Agent(
            role='Head First Technical Writer',
            goal='Write engaging, humorous, and visual content for a specific sub-section, adhering to the "Head First" style.',
            backstory=(
                "You are the reincarnation of the best technical writer who ever lived. "
                "You despise boring textbooks. You believe in learning through analogies, visuals, and humor. "
                "You write in a conversational tone, using 'we' and 'you'. "
                "You never just explain a concept; you tell a story about it. "
                "You are writing a section for a book on AI Agents."
            ),
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def reviewer(self):
        return Agent(
            role='Technical Reviewer',
            goal='Critique the written content for technical accuracy, clarity, and style adherence.',
            backstory=(
                "You are a eagle-eyed technical editor. You spot hallucinations, vague explanations, and boring prose from a mile away. "
                "You are also the guardian of the 'Head First' style. "
                "If a section is too dry, you flag it. "
                "If an analogy doesn't make sense, you flag it. "
                "You provide constructive, specific feedback."
            ),
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def editor(self):
        return Agent(
            role='Chief Editor',
            goal='Finalize the content by incorporating reviewer feedback and formatting it perfectly.',
            backstory=(
                "You are the final gatekeeper. You take the raw draft and the reviewer's notes "
                "and polish the text into a shining diamond. "
                "You ensure the formatting is perfect Markdown. "
                "You ensure the word count target is met. "
                "You make the final decision on what goes into the book."
            ),
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def formatter(self):
        return Agent(
            role='Consistency & Formatting Expert',
            goal='Ensure all chapters in the book follow identical formatting rules for titles, subtitles, code blocks, and diagrams.',
            backstory=(
                "You are a perfectionist with an eye for detail. Your job is to make sure the entire book "
                "feels like a single, cohesive unit. You check that Chapter titles use H1, "
                "Section titles use H2, and sub-sections use H3. You ensure that every 'Head First' "
                "element (like 'There Are No Dumb Questions') looks exactly the same in every chapter. "
                "You don't change the content, just the 'look and feel' of the Markdown."
            ),
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

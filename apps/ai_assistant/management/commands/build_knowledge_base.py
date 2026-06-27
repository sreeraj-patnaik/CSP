from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Build or rebuild the FAISS knowledge base for the AI assistant"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force rebuild even if KB already exists",
        )

    def handle(self, *args, **options):
        try:
            from apps.ai_assistant.rag import build_knowledge_base

            self.stdout.write("Building knowledge base...")
            result = build_knowledge_base()
            self.stdout.write(self.style.SUCCESS(f"Success: {result}"))
        except ImportError as error:
            self.stderr.write(
                self.style.WARNING(
                    f"LangChain not installed - skipping. ({error})\n"
                    "Run: pip install -r requirements.txt"
                )
            )
        except Exception as error:
            self.stderr.write(self.style.ERROR(f"Failed: {error}"))

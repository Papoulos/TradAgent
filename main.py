import argparse
from agents.preprocessing import create_glossary, evaluate_glossary
from dotenv import load_dotenv

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description='Traduction tool using LangChain and LangExtract.')
    parser.add_argument('--step', type=str, help='The step to run (preprocessing, translate, etc.).')
    parser.add_argument('--source', type=str, help='The source file to translate.')
    args = parser.parse_args()

    if args.step == 'preprocessing':
        if not args.source:
            print("Please specify a source file using --source.")
            return

        print("Running preprocessing step...")
        with open(args.source, 'r', encoding='utf-8') as f:
            source_text = f.read()

        glossary = create_glossary(source_text)
        print("Generated Glossary:")
        print(glossary)

        if glossary:
            evaluation = evaluate_glossary(glossary)
            print("\nGlossary Evaluation:")
            print(evaluation)

    elif args.step == 'translate':
        print("Running translation step...")
        # Add translation logic here
    else:
        print("Please specify a valid step.")

if __name__ == '__main__':
    main()

import argparse
import json
import os
from agents.preprocessing import create_glossary
from agents.profiling import create_author_profile
from agents.splitting import split_text
from agents.translation import translate_text
from dotenv import load_dotenv

load_dotenv()


def main():
    parser = argparse.ArgumentParser(description='Traduction tool using LangChain and LangExtract.')
    parser.add_argument('--step', type=str, help='The step to run (preprocessing, profile, translate, etc.).')
    parser.add_argument('--source', type=str, help='The source file to translate.')
    parser.add_argument('--author', type=str, help='The author of the source file.')
    args = parser.parse_args()

    if args.step == 'preprocessing':
        if not args.source:
            print("Please specify a source file using --source.")
            return

        print("Running preprocessing step...")
        with open(args.source, 'r', encoding='utf-8') as f:
            source_text = f.read()

        glossary = create_glossary(source_text)

        if glossary:
            # Save the glossary to a file
            base_name = os.path.splitext(args.source)[0]
            glossary_filename = f"{base_name}_glossary.json"
            with open(glossary_filename, 'w', encoding='utf-8') as f:
                json.dump(glossary, f, ensure_ascii=False, indent=4)
            print(f"\n✅ Glossary saved to {glossary_filename}")

        else:
            print("Glossary generation failed.")

    elif args.step == 'profile':
        if not args.source:
            print("Please specify a source file using --source.")
            return
        if not args.author:
            print("Please specify an author using --author.")
            return

        print("Running author profiling step...")
        with open(args.source, 'r', encoding='utf-8') as f:
            source_text = f.read()

        profile = create_author_profile(args.author, source_text)

        if profile:
            base_name = os.path.splitext(args.source)[0]
            profile_filename = f"{base_name}_profile.json"
            with open(profile_filename, 'w', encoding='utf-8') as f:
                json.dump(profile, f, ensure_ascii=False, indent=4)
            print(f"\n✅ Author profile saved to {profile_filename}")
        else:
            print("Author profiling failed.")

    elif args.step == 'translate':
        if not args.source:
            print("Please specify a source file using --source.")
            return

        print("Running translation step...")
        base_name = os.path.splitext(args.source)[0]
        glossary_filename = f"{base_name}_glossary.json"
        profile_filename = f"{base_name}_profile.json"
        translated_filename = f"{base_name}_translated.txt"

        try:
            with open(args.source, 'r', encoding='utf-8') as f:
                source_text = f.read()
            with open(glossary_filename, 'r', encoding='utf-8') as f:
                glossary = json.load(f)
            with open(profile_filename, 'r', encoding='utf-8') as f:
                author_profile = json.load(f)
        except FileNotFoundError as e:
            print(f"Error: Could not find a required file: {e.filename}")
            print("Please run the 'preprocessing' and 'profile' steps first.")
            return

        text_blocks = split_text(source_text)
        translated_text = translate_text(text_blocks, glossary, author_profile)

        with open(translated_filename, 'w', encoding='utf-8') as f:
            f.write(translated_text)
        print(f"\n✅ Translated text saved to {translated_filename}")

    else:
        print("Please specify a valid step.")

if __name__ == '__main__':
    main()

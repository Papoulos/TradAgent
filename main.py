import argparse
import json
import os
from agents.preprocessing import create_glossary
from agents.profiling import create_author_profile
from agents.splitting import split_text
from agents.translation import translate_text
from dotenv import load_dotenv
import config

load_dotenv()


def main():
    parser = argparse.ArgumentParser(description='Traduction tool using LangChain and LangExtract.')
    parser.add_argument('--step', type=str, required=True, help='The step to run (preprocessing, profile, translate).')
    parser.add_argument('--source', type=str, required=True, help='The source file to translate.')
    parser.add_argument('--author', type=str, help='The author of the source file (required for the "profile" step).')
    parser.add_argument('--max-blocks', type=int, help='The maximum number of blocks to translate.')
    args = parser.parse_args()

    # Create a dedicated directory for the translation project
    project_dir = os.path.splitext(args.source)[0]
    os.makedirs(project_dir, exist_ok=True)

    if args.step == 'preprocessing':
        profile_filename = os.path.join(project_dir, f"{os.path.basename(project_dir)}_profile.json")
        if not os.path.exists(profile_filename):
            print("Error: The profile file does not exist. Please run the 'profile' step first.")
            return

        print("Running preprocessing step...")
        with open(args.source, 'r', encoding='utf-8') as f:
            source_text = f.read()

        with open(profile_filename, 'r', encoding='utf-8') as f:
            author_profile = json.load(f)

        glossary = create_glossary(source_text, author_profile)

        if glossary:
            glossary_filename = os.path.join(project_dir, f"{os.path.basename(project_dir)}_glossary.json")
            with open(glossary_filename, 'w', encoding='utf-8') as f:
                json.dump(glossary, f, ensure_ascii=False, indent=4)
            print(f"\n✅ Glossary saved to {glossary_filename}")
        else:
            print("Glossary generation failed.")

    elif args.step == 'profile':
        if not args.author:
            print("Please specify an author using --author for the 'profile' step.")
            return

        print(f"Running author profiling step for {args.author}...")
        with open(args.source, 'r', encoding='utf-8') as f:
            source_text = f.read()

        profile = create_author_profile(args.author, source_text)

        if profile:
            profile_filename = os.path.join(project_dir, f"{os.path.basename(project_dir)}_profile.json")
            with open(profile_filename, 'w', encoding='utf-8') as f:
                json.dump(profile, f, ensure_ascii=False, indent=4)
            print(f"\n✅ Author profile saved to {profile_filename}")
        else:
            print("Author profiling failed.")

    elif args.step == 'translate':
        glossary_filename = os.path.join(project_dir, f"{os.path.basename(project_dir)}_glossary.json")
        profile_filename = os.path.join(project_dir, f"{os.path.basename(project_dir)}_profile.json")
        translated_filename = os.path.join(project_dir, f"{os.path.basename(project_dir)}_translated.txt")

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
        translated_text = translate_text(text_blocks, glossary, author_profile, args.max_blocks)

        with open(translated_filename, 'w', encoding='utf-8') as f:
            f.write(translated_text)
        print(f"\n✅ Translated text saved to {translated_filename}")

    else:
        print(f"Unknown step: {args.step}. Please choose from 'preprocessing', 'profile', or 'translate'.")

if __name__ == '__main__':
    main()

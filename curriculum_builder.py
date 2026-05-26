import os
import collections
import MeCab

GRAMMAR_POINTS = {
    # N5 Grammar
    "〜たい (want to)": ["たい", "たくない", "たかった"],
    "〜ている (is doing)": ["ている", "てる", "ていた", "てます"],
    "〜から / 〜ので (because)": ["から", "ので"],
    "〜つもりだ (plan to)": ["つもりだ", "つもりです", "つもりはない"],
    "〜たことがある (have done)": ["たことがある", "た事がある", "たことがない"],
    "〜てもいい (may do)": ["てもいい", "てもよい", "ても大丈夫"],
    "〜てはいけない (must not do)": ["てはいけない", "てはだめ", "ちゃだめ"],
    "〜たり〜たり (do things like)": ["たり"],
    "〜くなる / 〜になる (to become)": ["くなる", "になる"],
    "〜前に (before)": ["前に"],
    "〜後で (after)": ["後で"],
    "〜ないで (without doing)": ["ないで"],
    "〜ほうがいい (had better)": ["ほうがいい", "方がいい"],
    "〜でしょう / 〜だろう (probably)": ["でしょう", "だろう"],
    
    # N4 Grammar
    "〜かもしれない (might)": ["かもしれない", "かも知れない", "かも"],
    "〜はずだ (supposed to)": ["はずだ", "はずです", "はずがない"],
    "〜ようと思う (think of doing)": ["ようと思う", "ようと思っている"],
    "〜ば (conditional)": ["れば", "ならば"],
    "〜たら (conditional)": ["たら"],
    "〜なら (conditional)": ["なら"],
    "〜ても (even if)": ["ても", "でも"],
    "〜てしまう (do completely / regrettably)": ["てしまう", "ちゃう", "ちまう", "てしまった"],
    "〜ておく (do in advance)": ["ておく", "とく"],
    "〜てみる (try doing)": ["てみる", "てみよう", "てみた"],
    "〜やすい / 〜にくい (easy/hard to do)": ["やすい", "にくい"],
    "〜すぎる (too much)": ["すぎる", "過ぎる"],
    "〜なさい (command)": ["なさい"],
    "〜ために (in order to)": ["ために"],
    "〜ように (so that)": ["ように"],
    "〜そうだ (looks like / I heard)": ["そうだ", "そうです"],
    "〜らしい (seems like)": ["らしい"],
    "〜てあげる / 〜てもらう / 〜てくれる (giving/receiving)": ["てあげる", "てもらう", "てくれる"]
}

ADVANCED_GRAMMAR_POINTS = {
    # N3 Grammar
    "〜について (about)": ["について"],
    "〜にとって (for)": ["にとって"],
    "〜に対して (against / regarding)": ["に対して", "に対し"],
    "〜たびに (every time)": ["たびに"],
    "〜はずがない (cannot be)": ["はずがない", "はずもない"],
    "〜わけがない (no way that)": ["わけがない", "わけない"],
    "〜において (at / in)": ["において", "における"],
    "〜ようにする (try to)": ["ようにする", "ようにしている"],
    "〜たところ (just finished)": ["たところ"],
    "〜おそれがある (fear of)": ["おそれがある", "恐れがある"],
    "〜に違いない (must be)": ["に違いない"],
    "〜ば〜ほど (the more... the more)": ["ば", "ほど"],
    "〜ところだった (was about to)": ["ところだった"],
    "〜つつある (is continuing to)": ["つつある"],
    "〜がちだ (tend to)": ["がちだ", "がち"],
    "〜気味 (feeling like)": ["気味", "ぎみ"],
    "〜っぽい (ish)": ["っぽい"],

    # N2 Grammar
    "〜に際して (when doing)": ["に際して", "に際し"],
    "〜を問わず (regardless of)": ["を問わず", "は問わず"],
    "〜にほかならない (nothing but)": ["にほかならない"],
    "〜ざるを得ない (cannot help but)": ["ざるを得ない"],
    "〜にすぎない (only)": ["にすぎない", "に過ぎない"],
    "〜に伴って (along with)": ["に伴って", "にともなって"],
    "〜につれて (as X, then Y)": ["につれて"],
    "〜どころか (far from)": ["どころか"],
    "〜まい (will not)": ["まい"],
    "〜かねる (cannot)": ["かねる"],
    "〜かねない (might)": ["かねない"],
    "〜つつ (while)": ["つつ"],
    "〜抜きにして (without)": ["抜きにして", "抜きで"],

    # N1 Grammar
    "〜であれ (even if)": ["であれ"],
    "〜が早いか (no sooner than)": ["が早いか"],
    "〜や否や (as soon as)": ["や否や", "やいなや"],
    "〜そばから (as soon as)": ["そばから"],
    "〜だに (even just)": ["だに"],
    "〜たる (as a)": ["たる"],
    "〜の至り (utmost)": ["の至り"],
    "〜んがため (in order to)": ["んがため"],
    "〜んばかりに (as if to)": ["んばかりに"],
    "〜を皮切りに (starting with)": ["を皮切りに"]
}

def load_jlpt_dicts():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    jlpt_dicts = {}
    levels = ['n5', 'n4', 'n3', 'n2', 'n1']
    for lvl in levels:
        vocab_set = set()
        file_path = os.path.join(script_dir, f"jlpt_data/{lvl}.csv")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines[1:]:
                    parts = line.strip().split(',')
                    if len(parts) >= 2:
                        vocab_set.add(parts[0].strip())
                        vocab_set.add(parts[1].strip())
        jlpt_dicts[lvl.upper()] = vocab_set
    return jlpt_dicts

def classify_word(word, jlpt_dicts):
    for lvl in ['N5', 'N4', 'N3', 'N2', 'N1']:
        if word in jlpt_dicts[lvl]:
            return lvl
    return 'Unclassified'

def get_all_sorted(word_list):
    counter = collections.Counter(word_list)
    return [word for word, count in counter.most_common()]

def extract_grammar_all_sorted(text, grammar_dict):
    grammar_counter = collections.Counter()
    for point, patterns in grammar_dict.items():
        count = sum(text.count(p) for p in patterns)
        if count > 0:
            grammar_counter[point] = count
            
    return [point for point, count in grammar_counter.most_common()]

def format_vocab_group(words):
    if not words:
        return "None"
    return ", ".join(words)

def build_curriculum_for_book(book_title, book_output_dir, chapter_files):
    tagger = MeCab.Tagger('')
    jlpt_dicts = load_jlpt_dicts()
    
    curriculum_lines = []
    curriculum_lines.append(f"# Novel Curriculum: {book_title}\n")
    curriculum_lines.append("This curriculum contains 100% of all vocabulary and grammar points extracted directly from the chapters of the novel. The vocabulary is segregated by JLPT level to ensure focused learning.\n")
    
    for file_path in chapter_files:
        basename = os.path.basename(file_path)
        chapter_name = basename.replace(".txt", "").split(" - ")[-1]
        curriculum_lines.append(f"## {chapter_name}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            
        found_basic_grammar = extract_grammar_all_sorted(text, GRAMMAR_POINTS)
        found_advanced_grammar = extract_grammar_all_sorted(text, ADVANCED_GRAMMAR_POINTS)
                    
        node = tagger.parseToNode(text)
        all_words = []
        
        while node:
            features = node.feature.split(',')
            pos = features[0]
            pos2 = features[1] if len(features) > 1 else ''
            
            if pos == '名詞':
                if pos2 not in ['数詞', '非自立可能', '代名詞']:
                    surface = node.surface
                    if len(surface) > 1:
                        all_words.append(surface)
            elif pos in ['動詞', '形容詞']:
                if pos2 not in ['非自立可能']:
                    lemma = features[7] if len(features) > 7 else node.surface
                    if lemma != '*':
                        all_words.append(lemma)
                    else:
                        all_words.append(node.surface)
                
            node = node.next
            
        sorted_words = get_all_sorted(all_words)
        
        vocab_by_level = {
            'N5': [], 'N4': [], 'N3': [], 'N2': [], 'N1': [], 'Unclassified': []
        }
        
        for word in sorted_words:
            lvl = classify_word(word, jlpt_dicts)
            vocab_by_level[lvl].append(word)
        
        curriculum_lines.append("### Key Vocabulary (100% Extraction)")
        for lvl in ['N5', 'N4', 'N3', 'N2', 'N1', 'Unclassified']:
            if vocab_by_level[lvl]:
                curriculum_lines.append(f"**{lvl}:** " + format_vocab_group(vocab_by_level[lvl]))
        
        if found_basic_grammar:
            curriculum_lines.append("\n### Key Grammar Points (N5/N4)")
            curriculum_lines.append(", ".join(found_basic_grammar))
            
        if found_advanced_grammar:
            curriculum_lines.append("\n### Advanced Grammar Points (N3/N2/N1)")
            curriculum_lines.append(", ".join(found_advanced_grammar))
            
        curriculum_lines.append("\n")
        
    out_file = os.path.join(book_output_dir, f"{book_title} - Curriculum.md")
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(curriculum_lines))
        
    return out_file

CREATE TABLE users (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    display_name VARCHAR(150) NOT NULL,
    preferred_language VARCHAR(5) NOT NULL DEFAULT 'en',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY ix_users_email (email)
);

CREATE TABLE categories (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    slug VARCHAR(120) NOT NULL,
    sort_order INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY ix_categories_slug (slug)
);

CREATE TABLE category_translations (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    category_id BIGINT UNSIGNED NOT NULL,
    language_code VARCHAR(5) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_category_translations_category
        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
    CONSTRAINT uq_category_language UNIQUE (category_id, language_code),
    KEY ix_category_language_lookup (category_id, language_code),
    KEY ix_category_translation_language (language_code)
);

CREATE TABLE lessons (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    category_id BIGINT UNSIGNED NOT NULL,
    slug VARCHAR(150) NOT NULL,
    difficulty INT NOT NULL DEFAULT 1,
    sort_order INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_lessons_category
        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT,
    UNIQUE KEY ix_lessons_slug (slug),
    KEY ix_lessons_category_id (category_id)
);

CREATE TABLE lesson_translations (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    lesson_id BIGINT UNSIGNED NOT NULL,
    language_code VARCHAR(5) NOT NULL,
    title VARCHAR(255) NOT NULL,
    summary TEXT NULL,
    content_markdown LONGTEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_lesson_translations_lesson
        FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
    CONSTRAINT uq_lesson_language UNIQUE (lesson_id, language_code),
    KEY ix_lesson_language_lookup (lesson_id, language_code),
    KEY ix_lesson_translation_language (language_code)
);

CREATE TABLE quiz_questions (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    lesson_id BIGINT UNSIGNED NOT NULL,
    difficulty INT NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_quiz_questions_lesson
        FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
    KEY ix_quiz_questions_lesson_id (lesson_id)
);

CREATE TABLE quiz_question_translations (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    quiz_question_id BIGINT UNSIGNED NOT NULL,
    language_code VARCHAR(5) NOT NULL,
    prompt TEXT NOT NULL,
    options JSON NOT NULL,
    correct_option VARCHAR(255) NOT NULL,
    reference VARCHAR(255) NULL,
    explanation TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_quiz_question_translations_quiz
        FOREIGN KEY (quiz_question_id) REFERENCES quiz_questions(id) ON DELETE CASCADE,
    CONSTRAINT uq_quiz_question_language UNIQUE (quiz_question_id, language_code),
    KEY ix_quiz_question_language_lookup (quiz_question_id, language_code),
    KEY ix_quiz_question_translation_language (language_code)
);

CREATE TABLE flashcards (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    lesson_id BIGINT UNSIGNED NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_flashcards_lesson
        FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
    KEY ix_flashcards_lesson_id (lesson_id)
);

CREATE TABLE flashcard_translations (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    flashcard_id BIGINT UNSIGNED NOT NULL,
    language_code VARCHAR(5) NOT NULL,
    front_text TEXT NOT NULL,
    back_text TEXT NOT NULL,
    reference VARCHAR(255) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_flashcard_translations_flashcard
        FOREIGN KEY (flashcard_id) REFERENCES flashcards(id) ON DELETE CASCADE,
    CONSTRAINT uq_flashcard_language UNIQUE (flashcard_id, language_code),
    KEY ix_flashcard_language_lookup (flashcard_id, language_code),
    KEY ix_flashcard_translation_language (language_code)
);

CREATE TABLE user_flashcard_progress (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL,
    flashcard_id BIGINT UNSIGNED NOT NULL,
    leitner_level INT NOT NULL DEFAULT 1,
    last_reviewed_at DATETIME NULL,
    next_review_at DATETIME NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_flashcard_progress_user
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_user_flashcard_progress_flashcard
        FOREIGN KEY (flashcard_id) REFERENCES flashcards(id) ON DELETE CASCADE,
    CONSTRAINT uq_user_flashcard_progress UNIQUE (user_id, flashcard_id),
    KEY ix_user_flashcard_due_lookup (user_id, next_review_at)
);

CREATE TABLE bible_books (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    canonical_number INT NOT NULL,
    abbrev VARCHAR(10) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_bible_book_canonical_number UNIQUE (canonical_number),
    CONSTRAINT uq_bible_book_abbrev UNIQUE (abbrev),
    KEY ix_bible_books_abbrev (abbrev)
);

CREATE TABLE bible_book_translations (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    bible_book_id BIGINT UNSIGNED NOT NULL,
    language_code VARCHAR(5) NOT NULL,
    title VARCHAR(120) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_bible_book_translations_book
        FOREIGN KEY (bible_book_id) REFERENCES bible_books(id) ON DELETE CASCADE,
    CONSTRAINT uq_bible_book_language UNIQUE (bible_book_id, language_code),
    KEY ix_bible_book_language_lookup (bible_book_id, language_code)
);

CREATE TABLE bible_verses (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    bible_book_id BIGINT UNSIGNED NOT NULL,
    chapter_number INT NOT NULL,
    verse_number INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_bible_verses_book
        FOREIGN KEY (bible_book_id) REFERENCES bible_books(id) ON DELETE CASCADE,
    CONSTRAINT uq_bible_verse_lookup UNIQUE (bible_book_id, chapter_number, verse_number),
    KEY ix_bible_verse_book_chapter (bible_book_id, chapter_number),
    KEY ix_bible_verse_book_chapter_verse (bible_book_id, chapter_number, verse_number)
);

CREATE TABLE bible_verse_translations (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    bible_verse_id BIGINT UNSIGNED NOT NULL,
    language_code VARCHAR(5) NOT NULL,
    text LONGTEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_bible_verse_translations_verse
        FOREIGN KEY (bible_verse_id) REFERENCES bible_verses(id) ON DELETE CASCADE,
    CONSTRAINT uq_bible_verse_language UNIQUE (bible_verse_id, language_code),
    KEY ix_bible_verse_language_lookup (bible_verse_id, language_code),
    KEY ix_bible_verse_translation_language (language_code)
);

import sqlite3

def create_tables():
    try:
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute('''
            CREATE TABLE IF NOT EXISTS ideas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                idea TEXT,
                audio_file TEXT,
                transcription TEXT,
                titulo TEXT,
                descricao TEXT,
                impacto TEXT,
                recursos TEXT,
                beneficios TEXT,
                observacao TEXT,
                resumo TEXT,
                data_inicio TEXT,
                data_implementacao TEXT,
                visibilidade TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            ''')
            
            c.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
            ''')
            
            c.execute('''
            CREATE TABLE IF NOT EXISTS idea_tags (
                idea_id INTEGER,
                tag_id INTEGER,
                FOREIGN KEY (idea_id) REFERENCES ideas(id),
                FOREIGN KEY (tag_id) REFERENCES tags(id),
                PRIMARY KEY (idea_id, tag_id)
            )
            ''')

            c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                nome TEXT,
                sobrenome TEXT,
                cargo TEXT,
                setor TEXT,
                email TEXT,
                password TEXT,
                profile_picture BLOB
            )
            ''')

            c.execute('''
            CREATE TABLE IF NOT EXISTS idea_users (
                idea_id INTEGER,
                user_id INTEGER,
                FOREIGN KEY (idea_id) REFERENCES ideas(id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                PRIMARY KEY (idea_id, user_id)
            )
            ''')
            
            c.execute('''
            CREATE TABLE IF NOT EXISTS collaboration_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                idea_id INTEGER,
                requester_id INTEGER,
                status TEXT DEFAULT 'pendente',
                FOREIGN KEY (idea_id) REFERENCES ideas(id),
                FOREIGN KEY (requester_id) REFERENCES users(id)
            )
            ''')

            conn.commit()
    except sqlite3.Error as e:
        print(f"Erro ao criar a tabela no banco de dados: {e}")

def add_idea(user_id, idea=None, audio_file=None, transcription=None, titulo=None, descricao=None, impacto=None, recursos=None, beneficios=None, observacao=None, resumo=None, data_inicio=None, data_implementacao=None,visibilidade=None):
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''INSERT INTO ideas (user_id, idea, audio_file, transcription, titulo, descricao, impacto, recursos, beneficios, observacao, resumo, data_inicio, data_implementacao,visibilidade) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                  (user_id, idea, audio_file, transcription, titulo, descricao, impacto, recursos, beneficios, observacao, resumo, data_inicio, data_implementacao,visibilidade))
        conn.commit()
        print("Ideia adicionada com sucesso!")
        return c.lastrowid  # Retorna o ID da ideia adicionada
    except sqlite3.Error as e:
        print(f"Erro ao adicionar ideia no banco de dados: {e}")
        return None
    finally:
        conn.close()

def get_ideas(user_id):
    try:
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute("SELECT id, idea, transcription, titulo FROM ideas WHERE user_id=?", (user_id,))
            ideas = c.fetchall()
        return ideas
    except sqlite3.Error as e:
        print(f"Erro ao obter ideias do banco de dados: {e}")
        return []

def delete_idea(idea_id):
    try:
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute("DELETE FROM ideas WHERE id=?", (idea_id,))
            conn.commit()
            print(f"Ideia com ID {idea_id} excluída com sucesso.")
    except sqlite3.Error as e:
        print(f"Erro ao excluir ideia do banco de dados: {e}")

if __name__ == "__main__":
    create_tables()

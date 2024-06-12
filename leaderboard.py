import sqlite3

CONNECTION = sqlite3.connect("leaderboard.db")
CURSOR = CONNECTION.cursor()

class Score:
    TARGET_POINTS = {
        'Cows': 8,
        'Chickens': 4,
        'People': 1,
        'Cars': lambda targets: 1 * targets['People'] + 4 * targets['Chickens'],
        'Best in Show Cow': 10,
    }

    ENEMY_POINTS = {
        'Military': -6,
        'Police': -4,
        'Conspiracy Theorist': -10,
        'FBI Agents': -20,
    }

    def __init__(self, player, game):
        self.player = player
        self.game = game
        self.targets = {key: 0 for key in self.TARGET_POINTS}
        self.enemies = {key: 0 for key in self.ENEMY_POINTS}

    @classmethod
    def create_table(cls):
        """ Create a new table for scores """
        sql = """
            CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            game_id INTEGER,
            target TEXT,
            count INTEGER,
            FOREIGN KEY(player_id) REFERENCES players(id),
            FOREIGN KEY(game_id) REFERENCES games(id))
        """
        CURSOR.execute(sql)
        CONNECTION.commit()

    def add_target(self, target, count=1):
        if target in self.targets:
            self.targets[target] += count

    def add_enemy(self, enemy, count=1):
        if enemy in self.enemies:
            self.enemies[enemy] += count

    def calculate_score(self):
        score = 0
        for target, count in self.targets.items():
            points = self.TARGET_POINTS[target]
            if callable(points):
                score += points(self.targets)
            else:
                score += points * count
        for enemy, count in self.enemies.items():
            score += self.ENEMY_POINTS[enemy] * count
        return score

    def save_score(self):
        """ Save score details to the database """
        for target, count in self.targets.items():
            sql = 'INSERT INTO scores (player_id, game_id, target, count) VALUES (?, ?, ?, ?)'
            CURSOR.execute(sql, (self.player.id, self.game.id, target, count))
            CONNECTION.commit()

        total_score = self.calculate_score()
        result = Result(self.player, self.game, total_score)
        result.save()

class Game:
    def __init__(self, title):
        self.title = title

    @classmethod
    def initialize_database(cls):
        cls.create_table()
        Player.create_table()
        Result.create_table()
        Score.create_table()

        placeholder_players = [
            ('LeMaiL', 125),
            ('BobtheBuilder', 111),
            ('Drizzo', 104),
            ('2LGIT2QUIT', 97),
            ('Evenflow', 95),
            ('FrankTheTank', 90),
            ('LukeSkyTalker', 70),
            ('HenryThe8th', 68),
            ('PoisonIvy', 60),
            ('JackTheR!pper', 52)
        ]

        for username, score in placeholder_players:
            player = Player(username=username)
            player.save()
            print(f"Inserted player: {player.username}, ID: {player.id}")  # Debug statement

            game = Game(title='Mû.F.O')  # Replace with your actual game title
            game.save()
            print(f"Inserted game: {game.title}, ID: {game.id}")  # Debug statement

            player_id = player.id
            game_id = game.id   

            # Create score and result entries
            score_entry = Score(player=player, game=game)
            score_entry.add_target('Cows', score // 8)  # Example target
            score_entry.save_score()
            print(f"Saved score for player: {player.username}, Score: {score_entry.calculate_score()}")  # Debug statement

    @classmethod
    def create_table(cls):
        """ Create a new table for games """
        sql = """
            CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL)
        """
        CURSOR.execute(sql)
        CONNECTION.commit()

    def save(self):
        """ Save a new game to the database """
        sql = 'INSERT OR IGNORE INTO games (title) VALUES (?)'
        CURSOR.execute(sql, (self.title,))
        CONNECTION.commit()
        self.id = CURSOR.lastrowid

class Player:
    def __init__(self, username, id=None):
        self.id = id
        self.username = username

    @classmethod
    def create_table(cls):
        """ Create a new table for players """
        sql = """
            CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL)
        """
        CURSOR.execute(sql)
        CONNECTION.commit()

    @classmethod
    def find_or_create(cls, username):
        """ Find existing player by username or create a new one """
        sql = "SELECT id FROM players WHERE username = ?"
        CURSOR.execute(sql, (username,))
        player_row = CURSOR.fetchone()
        
        if player_row:
            player_id = player_row[0]
        else:
            sql = "INSERT INTO players (username) VALUES (?)"
            CURSOR.execute(sql, (username,))
            CONNECTION.commit()
            player_id = CURSOR.lastrowid
        
        return cls(username=username, id=player_id)

    def save(self):
        """ Save a new player to the database """
        sql = 'INSERT OR IGNORE INTO players (username) VALUES (?)'
        CURSOR.execute(sql, (self.username,))
        CONNECTION.commit()
        self.id = CURSOR.lastrowid

class Result:
    all = []

    def __init__(self, player, game, score):
        self.player = player
        self.game = game
        self.score = score
        Result.all.append(self)

    @classmethod
    def create_table(cls):
        """ Create a new table for results """
        sql = """
            CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            game_id INTEGER,
            score INTEGER,
            FOREIGN KEY(player_id) REFERENCES players(id),
            FOREIGN KEY(game_id) REFERENCES games(id))
        """
        CURSOR.execute(sql)
        CONNECTION.commit()

    def save(self):
        """ Save a new result to the database """
        sql = 'INSERT INTO results (player_id, game_id, score) VALUES (?, ?, ?)'
        CURSOR.execute(sql, (self.player.id, self.game.id, self.score))
        CONNECTION.commit()

    @classmethod
    def get_leaderboard(cls):
        """ Retrieve the leaderboard data """
        sql = """
            SELECT p.username, g.title, r.score 
            FROM results r
            JOIN players p ON r.player_id = p.id
            JOIN games g ON r.game_id = g.id
            ORDER BY r.score DESC
            LIMIT 10
        """
        CURSOR.execute(sql)
        results = CURSOR.fetchall()
        print(f"Leaderboard data: {results}")  # Debug statement
        return results

# Initialize the database
Game.initialize_database()


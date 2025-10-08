# backend.py - Mpho Mafolo Academy Backend API
# Run this file first: python backend.py

import mysql.connector
from mysql.connector import Error
from datetime import datetime, date
from flask import Flask, request, jsonify
from flask_cors import CORS

class MphoAcademyDatabase:
    def __init__(self, host='localhost', database='mpho_academy', user='root', password=''):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        
    def create_connection(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            if self.connection.is_connected():
                print("✓ Successfully connected to MySQL database")
                return True
        except Error as e:
            print(f"✗ Error connecting to MySQL: {e}")
            return False
    
    def create_database_and_tables(self):
        try:
            temp_connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            cursor = temp_connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            print(f"✓ Database '{self.database}' ready")
            cursor.close()
            temp_connection.close()
            
            if self.create_connection():
                cursor = self.connection.cursor()
                
                create_players_table = """
                CREATE TABLE IF NOT EXISTS players (
                    player_id INT AUTO_INCREMENT PRIMARY KEY,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    date_of_birth DATE NOT NULL,
                    age INT,
                    gender ENUM('Male', 'Female', 'Other') DEFAULT 'Male',
                    position VARCHAR(30),
                    email VARCHAR(100),
                    phone VARCHAR(20) NOT NULL,
                    parent_guardian_name VARCHAR(100),
                    parent_phone VARCHAR(20),
                    emergency_contact VARCHAR(20),
                    address TEXT,
                    medical_info TEXT,
                    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status ENUM('Active', 'Inactive', 'Suspended') DEFAULT 'Active',
                    jersey_number INT UNIQUE,
                    joining_fee_paid BOOLEAN DEFAULT FALSE,
                    monthly_fee_paid BOOLEAN DEFAULT FALSE,
                    notes TEXT,
                    INDEX idx_name (first_name, last_name),
                    INDEX idx_position (position),
                    INDEX idx_status (status)
                )
                """
                cursor.execute(create_players_table)
                self.connection.commit()
                print("✓ Tables created successfully")
                cursor.close()
                
        except Error as e:
            print(f"✗ Error creating database/tables: {e}")
    
    def calculate_age(self, birth_date):
        today = date.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    
    def add_player(self, player_data):
        if not self.connection or not self.connection.is_connected():
            self.create_connection()
        
        try:
            cursor = self.connection.cursor()
            birth_date = datetime.strptime(player_data['date_of_birth'], '%Y-%m-%d').date()
            age = self.calculate_age(birth_date)
            
            insert_query = """
            INSERT INTO players (
                first_name, last_name, date_of_birth, age, gender, position,
                email, phone, parent_guardian_name, parent_phone, emergency_contact,
                address, medical_info, jersey_number, joining_fee_paid, notes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                player_data['first_name'],
                player_data['last_name'],
                player_data['date_of_birth'],
                age,
                player_data.get('gender', 'Male'),
                player_data.get('position', ''),
                player_data.get('email', ''),
                player_data['phone'],
                player_data.get('parent_guardian_name', ''),
                player_data.get('parent_phone', ''),
                player_data.get('emergency_contact', ''),
                player_data.get('address', ''),
                player_data.get('medical_info', ''),
                player_data.get('jersey_number'),
                player_data.get('joining_fee_paid', False),
                player_data.get('notes', '')
            )
            
            cursor.execute(insert_query, values)
            self.connection.commit()
            player_id = cursor.lastrowid
            cursor.close()
            print(f"✓ Player added: {player_data['first_name']} {player_data['last_name']}")
            return player_id
            
        except Error as e:
            print(f"✗ Error adding player: {e}")
            return None
    
    def get_all_players(self, status='Active'):
        if not self.connection or not self.connection.is_connected():
            self.create_connection()
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            if status == 'All':
                query = "SELECT * FROM players ORDER BY registration_date DESC"
                cursor.execute(query)
            else:
                query = "SELECT * FROM players WHERE status = %s ORDER BY registration_date DESC"
                cursor.execute(query, (status,))
            
            players = cursor.fetchall()
            cursor.close()
            
            for player in players:
                if player['date_of_birth']:
                    player['date_of_birth'] = player['date_of_birth'].strftime('%Y-%m-%d')
                if player['registration_date']:
                    player['registration_date'] = player['registration_date'].strftime('%Y-%m-%d %H:%M:%S')
            
            return players
            
        except Error as e:
            print(f"✗ Error retrieving players: {e}")
            return []
    
    def search_players(self, search_term):
        if not self.connection or not self.connection.is_connected():
            self.create_connection()
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            search_query = """
            SELECT * FROM players 
            WHERE first_name LIKE %s 
               OR last_name LIKE %s 
               OR position LIKE %s 
               OR phone LIKE %s 
               OR CONCAT(first_name, ' ', last_name) LIKE %s
            ORDER BY first_name, last_name
            """
            
            search_pattern = f"%{search_term}%"
            cursor.execute(search_query, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))
            
            players = cursor.fetchall()
            cursor.close()
            
            for player in players:
                if player['date_of_birth']:
                    player['date_of_birth'] = player['date_of_birth'].strftime('%Y-%m-%d')
                if player['registration_date']:
                    player['registration_date'] = player['registration_date'].strftime('%Y-%m-%d %H:%M:%S')
            
            return players
            
        except Error as e:
            print(f"✗ Error searching players: {e}")
            return []
    
    def delete_player(self, player_id):
        if not self.connection or not self.connection.is_connected():
            self.create_connection()
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT first_name, last_name FROM players WHERE player_id = %s", (player_id,))
            player = cursor.fetchone()
            
            if not player:
                return False
            
            delete_query = "DELETE FROM players WHERE player_id = %s"
            cursor.execute(delete_query, (player_id,))
            self.connection.commit()
            cursor.close()
            print(f"✓ Player deleted: {player[0]} {player[1]}")
            return True
            
        except Error as e:
            print(f"✗ Error deleting player: {e}")
            return False
    
    def get_academy_stats(self):
        if not self.connection or not self.connection.is_connected():
            self.create_connection()
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            cursor.execute("SELECT COUNT(*) as total FROM players")
            total = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as active FROM players WHERE status = 'Active'")
            active = cursor.fetchone()['active']
            
            cursor.execute("""
                SELECT position, COUNT(*) as count 
                FROM players 
                WHERE position != '' AND status = 'Active'
                GROUP BY position
            """)
            positions = cursor.fetchall()
            
            cursor.execute("""
                SELECT COUNT(*) as recent 
                FROM players 
                WHERE registration_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            """)
            recent = cursor.fetchone()['recent']
            
            cursor.close()
            
            return {
                'total_players': total,
                'active_players': active,
                'inactive_players': total - active,
                'recent_registrations': recent,
                'positions_breakdown': positions
            }
            
        except Error as e:
            print(f"✗ Error getting stats: {e}")
            return {}
    
    def close_connection(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")

# Flask API Application
app = Flask(__name__)
CORS(app)

# Initialize database - CHANGE PASSWORD HERE
db = MphoAcademyDatabase(
    host='localhost',
    database='mpho_academy', 
    user='root',
    password=''  # PUT YOUR MYSQL PASSWORD HERE
)

# API Routes
@app.route('/api/stats')
def get_stats():
    stats = db.get_academy_stats()
    return jsonify(stats)

@app.route('/api/players', methods=['GET'])
def get_players():
    status = request.args.get('status', 'All')
    players = db.get_all_players(status)
    return jsonify(players)

@app.route('/api/players/search')
def search_players():
    search_term = request.args.get('q', '')
    players = db.search_players(search_term)
    return jsonify(players)

@app.route('/api/players', methods=['POST'])
def add_player():
    try:
        player_data = request.get_json()
        player_id = db.add_player(player_data)
        
        if player_id:
            return jsonify({'success': True, 'player_id': player_id})
        else:
            return jsonify({'success': False, 'message': 'Failed to add player'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/players/<int:player_id>', methods=['DELETE'])
def delete_player(player_id):
    try:
        success = db.delete_player(player_id)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🏆 MPHO MAFOLO ACADEMY - BACKEND SERVER")
    print("="*50)
    print("\nSetting up database...")
    db.create_database_and_tables()
    
    print("\n" + "="*50)
    print("✓ Backend server starting...")
    print("="*50)
    print("\n📡 API will be available at:")
    print("   http://localhost:5000")
    print("\n⚠️  Keep this terminal window open!")
    print("="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
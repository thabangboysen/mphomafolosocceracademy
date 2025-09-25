# Mpho Mafolo Academy - Player Database System
# Requirements: pip install mysql-connector-python flask flask-cors

import mysql.connector
from mysql.connector import Error
from datetime import datetime, date
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json

class MphoAcademyDatabase:
    def __init__(self, host='localhost', database='mpho_academy', user='root', password=''):
        """
        Initialize the database connection
        
        Args:
            host: MySQL server host (default: localhost)
            database: Database name (default: mpho_academy)
            user: MySQL username (default: root)
            password: MySQL password (default: empty)
        """
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        
    def create_connection(self):
        """Create a database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            if self.connection.is_connected():
                print("Successfully connected to MySQL database")
                return True
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
            return False
    
    def create_database_and_tables(self):
        """Create the database and required tables"""
        try:
            # Connect to MySQL server (without specifying database)
            temp_connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            cursor = temp_connection.cursor()
            
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            print(f"Database '{self.database}' created successfully")
            
            cursor.close()
            temp_connection.close()
            
            # Now connect to the specific database
            if self.create_connection():
                cursor = self.connection.cursor()
                
                # Create players table
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
                
                # Create a statistics table for academy overview
                create_stats_table = """
                CREATE TABLE IF NOT EXISTS academy_stats (
                    id INT PRIMARY KEY DEFAULT 1,
                    total_players INT DEFAULT 0,
                    active_players INT DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
                """
                cursor.execute(create_stats_table)
                
                # Insert initial stats record
                cursor.execute("INSERT IGNORE INTO academy_stats (id) VALUES (1)")
                
                self.connection.commit()
                print("Tables created successfully")
                cursor.close()
                
        except Error as e:
            print(f"Error creating database/tables: {e}")
    
    def calculate_age(self, birth_date):
        """Calculate age from birth date"""
        today = date.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    
    def add_player(self, player_data):
        """
        Add a new player to the database
        
        Args:
            player_data: Dictionary containing player information
        
        Returns:
            int: Player ID if successful, None if failed
        """
        if not self.connection or not self.connection.is_connected():
            self.create_connection()
        
        try:
            cursor = self.connection.cursor()
            
            # Calculate age from date of birth
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
            self.update_academy_stats()
            
            cursor.close()
            print(f"Player {player_data['first_name']} {player_data['last_name']} added successfully with ID: {player_id}")
            return player_id
            
        except Error as e:
            print(f"Error adding player: {e}")
            return None
    
    def get_all_players(self, status='Active'):
        """
        Retrieve all players from the database
        
        Args:
            status: Filter by status ('Active', 'Inactive', 'Suspended', or 'All')
        
        Returns:
            list: List of player records
        """
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
            
            # Convert date objects to strings for JSON serialization
            for player in players:
                if player['date_of_birth']:
                    player['date_of_birth'] = player['date_of_birth'].strftime('%Y-%m-%d')
                if player['registration_date']:
                    player['registration_date'] = player['registration_date'].strftime('%Y-%m-%d %H:%M:%S')
            
            return players
            
        except Error as e:
            print(f"Error retrieving players: {e}")
            return []
    
    def search_players(self, search_term):
        """
        Search for players by name, position, or phone
        
        Args:
            search_term: Search term
        
        Returns:
            list: List of matching players
        """
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
            
            # Convert date objects to strings
            for player in players:
                if player['date_of_birth']:
                    player['date_of_birth'] = player['date_of_birth'].strftime('%Y-%m-%d')
                if player['registration_date']:
                    player['registration_date'] = player['registration_date'].strftime('%Y-%m-%d %H:%M:%S')
            
            return players
            
        except Error as e:
            print(f"Error searching players: {e}")
            return []
    
    def get_player_by_id(self, player_id):
        """Get a specific player by ID"""
        if not self.connection or not self.connection.is_connected():
            self.create_connection()
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM players WHERE player_id = %s"
            cursor.execute(query, (player_id,))
            
            player = cursor.fetchone()
            cursor.close()
            
            if player:
                if player['date_of_birth']:
                    player['date_of_birth'] = player['date_of_birth'].strftime('%Y-%m-%d')
                if player['registration_date']:
                    player['registration_date'] = player['registration_date'].strftime('%Y-%m-%d %H:%M:%S')
            
            return player
            
        except Error as e:
            print(f"Error retrieving player: {e}")
            return None
    
    def update_player(self, player_id, update_data):
        """Update player information"""
        if not self.connection or not self.connection.is_connected():
            self.create_connection()
        
        try:
            cursor = self.connection.cursor()
            
            # Build dynamic update query
            set_clauses = []
            values = []
            
            for key, value in update_data.items():
                if key != 'player_id':
                    set_clauses.append(f"{key} = %s")
                    values.append(value)
            
            if not set_clauses:
                return False
            
            # Recalculate age if date_of_birth is updated
            if 'date_of_birth' in update_data:
                birth_date = datetime.strptime(update_data['date_of_birth'], '%Y-%m-%d').date()
                age = self.calculate_age(birth_date)
                set_clauses.append("age = %s")
                values.append(age)
            
            values.append(player_id)
            
            update_query = f"UPDATE players SET {', '.join(set_clauses)} WHERE player_id = %s"
            cursor.execute(update_query, values)
            
            self.connection.commit()
            cursor.close()
            
            print(f"Player {player_id} updated successfully")
            return True
            
        except Error as e:
            print(f"Error updating player: {e}")
            return False
    
    def delete_player(self, player_id):
        """Delete a player from the database"""
        if not self.connection or not self.connection.is_connected():
            self.create_connection()
        
        try:
            cursor = self.connection.cursor()
            
            # First get player name for confirmation
            cursor.execute("SELECT first_name, last_name FROM players WHERE player_id = %s", (player_id,))
            player = cursor.fetchone()
            
            if not player:
                print("Player not found")
                return False
            
            # Delete the player
            delete_query = "DELETE FROM players WHERE player_id = %s"
            cursor.execute(delete_query, (player_id,))
            
            self.connection.commit()
            self.update_academy_stats()
            
            cursor.close()
            print(f"Player {player[0]} {player[1]} deleted successfully")
            return True
            
        except Error as e:
            print(f"Error deleting player: {e}")
            return False
    
    def get_academy_stats(self):
        """Get academy statistics"""
        if not self.connection or not self.connection.is_connected():
            self.create_connection()
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # Get total players
            cursor.execute("SELECT COUNT(*) as total FROM players")
            total = cursor.fetchone()['total']
            
            # Get active players
            cursor.execute("SELECT COUNT(*) as active FROM players WHERE status = 'Active'")
            active = cursor.fetchone()['active']
            
            # Get players by position
            cursor.execute("""
                SELECT position, COUNT(*) as count 
                FROM players 
                WHERE position != '' AND status = 'Active'
                GROUP BY position
            """)
            positions = cursor.fetchall()
            
            # Get recent registrations (last 30 days)
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
            print(f"Error getting stats: {e}")
            return {}
    
    def update_academy_stats(self):
        """Update the academy statistics table"""
        try:
            cursor = self.connection.cursor()
            
            # Count total and active players
            cursor.execute("SELECT COUNT(*) FROM players")
            total = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM players WHERE status = 'Active'")
            active = cursor.fetchone()[0]
            
            # Update stats table
            cursor.execute("""
                UPDATE academy_stats 
                SET total_players = %s, active_players = %s, last_updated = NOW() 
                WHERE id = 1
            """, (total, active))
            
            self.connection.commit()
            cursor.close()
            
        except Error as e:
            print(f"Error updating stats: {e}")
    
    def close_connection(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")

# Flask Web Application
app = Flask(__name__)
CORS(app)

# Initialize database
db = MphoAcademyDatabase(
    host='localhost',
    database='mpho_academy', 
    user='root',
    password='Rakgalakane@01'
)

# Web interface HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Mpho Mafolo Academy - Database</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; color: #333; margin-bottom: 30px; }
        .stats { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .form { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .players-list { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        input, select, textarea { width: 100%; padding: 8px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px; }
        button { background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
        button:hover { background-color: #0056b3; }
        .player-card { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 8px; background: #f9f9f9; }
        .search-bar { width: 100%; padding: 12px; font-size: 16px; border: 2px solid #ddd; border-radius: 4px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚽ Mpho Mafolo Academy</h1>
            <h2>Player Database Management</h2>
        </div>
        
        <div class="stats">
            <h3>Academy Statistics</h3>
            <div id="stats-content">Loading...</div>
        </div>
        
        <div class="form">
            <h3>Add New Player</h3>
            <form id="playerForm">
                <input type="text" id="firstName" placeholder="First Name *" required>
                <input type="text" id="lastName" placeholder="Last Name *" required>
                <input type="date" id="dateOfBirth" required>
                <select id="gender">
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                </select>
                <select id="position">
                    <option value="">Select Position</option>
                    <option value="Goalkeeper">Goalkeeper</option>
                    <option value="Defender">Defender</option>
                    <option value="Midfielder">Midfielder</option>
                    <option value="Forward">Forward</option>
                </select>
                <input type="email" id="email" placeholder="Email">
                <input type="tel" id="phone" placeholder="Phone Number *" required>
                <input type="text" id="parentName" placeholder="Parent/Guardian Name">
                <input type="tel" id="parentPhone" placeholder="Parent Phone">
                <input type="tel" id="emergencyContact" placeholder="Emergency Contact">
                <textarea id="address" placeholder="Address" rows="3"></textarea>
                <textarea id="medicalInfo" placeholder="Medical Information" rows="2"></textarea>
                <input type="number" id="jerseyNumber" placeholder="Jersey Number">
                <textarea id="notes" placeholder="Additional Notes" rows="2"></textarea>
                <button type="submit">Add Player</button>
            </form>
        </div>
        
        <div class="players-list">
            <h3>Registered Players</h3>
            <input type="text" class="search-bar" id="searchInput" placeholder="Search players...">
            <div id="players-content">Loading...</div>
        </div>
    </div>

    <script>
        // Load stats and players on page load
        window.onload = function() {
            loadStats();
            loadPlayers();
        };

        // Form submission
        document.getElementById('playerForm').addEventListener('submit', function(e) {
            e.preventDefault();
            addPlayer();
        });

        // Search functionality
        document.getElementById('searchInput').addEventListener('input', function() {
            const searchTerm = this.value;
            if (searchTerm.length > 2) {
                searchPlayers(searchTerm);
            } else if (searchTerm.length === 0) {
                loadPlayers();
            }
        });

        function addPlayer() {
            const formData = {
                first_name: document.getElementById('firstName').value,
                last_name: document.getElementById('lastName').value,
                date_of_birth: document.getElementById('dateOfBirth').value,
                gender: document.getElementById('gender').value,
                position: document.getElementById('position').value,
                email: document.getElementById('email').value,
                phone: document.getElementById('phone').value,
                parent_guardian_name: document.getElementById('parentName').value,
                parent_phone: document.getElementById('parentPhone').value,
                emergency_contact: document.getElementById('emergencyContact').value,
                address: document.getElementById('address').value,
                medical_info: document.getElementById('medicalInfo').value,
                jersey_number: document.getElementById('jerseyNumber').value || null,
                notes: document.getElementById('notes').value
            };

            fetch('/api/players', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Player added successfully!');
                    document.getElementById('playerForm').reset();
                    loadStats();
                    loadPlayers();
                } else {
                    alert('Error adding player: ' + data.message);
                }
            });
        }

        function loadStats() {
            fetch('/api/stats')
            .then(response => response.json())
            .then(data => {
                const statsHtml = `
                    <p><strong>Total Players:</strong> ${data.total_players}</p>
                    <p><strong>Active Players:</strong> ${data.active_players}</p>
                    <p><strong>Recent Registrations (30 days):</strong> ${data.recent_registrations}</p>
                `;
                document.getElementById('stats-content').innerHTML = statsHtml;
            });
        }

        function loadPlayers() {
            fetch('/api/players')
            .then(response => response.json())
            .then(data => {
                displayPlayers(data);
            });
        }

        function searchPlayers(searchTerm) {
            fetch(`/api/players/search?q=${encodeURIComponent(searchTerm)}`)
            .then(response => response.json())
            .then(data => {
                displayPlayers(data);
            });
        }

        function displayPlayers(players) {
            const playersHtml = players.map(player => `
                <div class="player-card">
                    <h4>${player.first_name} ${player.last_name}</h4>
                    <p><strong>Age:</strong> ${player.age} | <strong>Position:</strong> ${player.position || 'Not specified'}</p>
                    <p><strong>Phone:</strong> ${player.phone} | <strong>Email:</strong> ${player.email || 'Not provided'}</p>
                    <p><strong>Parent:</strong> ${player.parent_guardian_name || 'Not provided'}</p>
                    <p><strong>Status:</strong> ${player.status} | <strong>Jersey:</strong> ${player.jersey_number || 'Not assigned'}</p>
                    <p><strong>Registered:</strong> ${player.registration_date}</p>
                    ${player.medical_info ? `<p><strong>Medical:</strong> ${player.medical_info}</p>` : ''}
                    <button onclick="deletePlayer(${player.player_id})" style="background-color: #dc3545;">Delete</button>
                </div>
            `).join('');
            
            document.getElementById('players-content').innerHTML = playersHtml || '<p>No players found.</p>';
        }

        function deletePlayer(playerId) {
            if (confirm('Are you sure you want to delete this player?')) {
                fetch(`/api/players/${playerId}`, {method: 'DELETE'})
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        loadStats();
                        loadPlayers();
                    } else {
                        alert('Error deleting player: ' + data.message);
                    }
                });
            }
        }
    </script>
</body>
</html>
"""

# API Routes
@app.route('/')
def index():
    return HTML_TEMPLATE

@app.route('/api/stats')
def get_stats():
    stats = db.get_academy_stats()
    return jsonify(stats)

@app.route('/api/players', methods=['GET'])
def get_players():
    status = request.args.get('status', 'Active')
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

@app.route('/api/players/<int:player_id>', methods=['PUT'])
def update_player(player_id):
    try:
        update_data = request.get_json()
        success = db.update_player(player_id, update_data)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    # Initialize database and tables
    print("Setting up Mpho Mafolo Academy Database...")
    db.create_database_and_tables()
    
    # Example usage
    print("\n--- Example Usage ---")
    
    # Add sample players
    sample_players = [
        {
            'first_name': 'Thabo',
            'last_name': 'Mthembu',
            'date_of_birth': '2010-03-15',
            'gender': 'Male',
            'position': 'Forward',
            'email': 'thabo@email.com',
            'phone': '0821234567',
            'parent_guardian_name': 'Sarah Mthembu',
            'parent_phone': '0831234567',
            'emergency_contact': '0831234567',
            'address': '123 Soccer Street, Johannesburg',
            'jersey_number': 10,
            'joining_fee_paid': True
        },
        {
            'first_name': 'Nomsa',
            'last_name': 'Dlamini',
            'date_of_birth': '2011-07-22',
            'gender': 'Female',
            'position': 'Midfielder',
            'phone': '0827654321',
            'parent_guardian_name': 'John Dlamini',
            'address': '456 Academy Road, Soweto'
        }
    ]
    
    for player in sample_players:
        db.add_player(player)
    
    # Display stats
    stats = db.get_academy_stats()
    print(f"\nAcademy Statistics:")
    print(f"Total Players: {stats['total_players']}")
    print(f"Active Players: {stats['active_players']}")
    
    # Search example
    search_results = db.search_players('Thabo')
    print(f"\nSearch results for 'Thabo': {len(search_results)} found")
    
    print("\nStarting Flask web server...")
    print("Visit http://localhost:5000 to access the web interface")
    
    # Start the web application
    app.run(debug=True, host='0.0.0.0', port=5000)
# Redis-Vote

Redis-Vote is a simple CLI application that simulates a proposal voting system by students. The students are the users who register and access the application.

## Setup

```bash
# Clone the repository
git clone https://github.com/MadMat00/redis-vote.git
# Navigate to the directory
cd redis-vote
# Install the required libraries
pip install -r requirements.txt
```

To use the application and connect to the Redis database, you need to create an `.env` file containing the HOST, PORT, and PASSWORD of the database:
```bash
touch .env
# Enter the following information
REDIS_HOST = <connection string>
REDIS_PORT = <redis port>
REDIS_PASSWORD = <redis password>
```


## How It Works

Run the program:
```bash
python main.py
```

The user has two initial options:

1. Login
2. Registration

After that, the user can choose various operations through a menu:

1. Create a new proposal
2. Vote on a proposal
3. View proposals
4. Exit the program

## Requirements

- A user can only give one vote to each proposal.
- The display is ordered by votes.

### Extra

The sklearn library was used to check for the insertion of similar proposals.

## Demo
<video width="630" height="300" src="https://drive.google.com/file/d/1-rbdY0ifwtalkxR3_mBVJLKpE0hbFDNt/view?usp=drive_link"></video>

## Redis

The proposal data and user information are managed with a Redis database.
Specifically, each proposal is stored in a hash (for the title and description) and a set (to store the users who voted for it). User information is stored in a hash.

## Authors

@MadMat00
@ItsAtlant
@nik-ashely
@MarcoPirrotta

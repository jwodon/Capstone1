# GameFinder

## Website URL: [GameFinder](https://your-website-url.com)

## Description

GameFinder is a platform where users can discover and explore various video games. Users can search for games based on different criteria such as platform and genre, view game details including ratings and reviews, and create and manage lists of their favorite games.

## Setup Instructions

1. **Clone the repository:**

2. **Navigate to the project directory:**

3. **Install dependencies:**

-   See requirements.txt

4. **Set up the PostgreSQL database:**

-   Create a PostgreSQL database named `capstone1`.
-   Update the `SQLALCHEMY_DATABASE_URI` in `app.py` if necessary.

5. **Run the Flask app:**

6. **Access the application:**
   Open a web browser and go to [http://localhost:5000](http://localhost:5000) to access the GameFinder application.

## Features

-   **User Authentication:** Users can sign up, log in, and log out securely.
-   **Game Search:** Users can search for games based on platforms and genres.
-   **Game Details:** Users can view detailed information about each game, including summaries, ratings, and available platforms.
-   **Rating System:** Users can rate games and view average ratings for each game.
-   **List Management:** Users can create and manage lists of their favorite games.
-   **API Integration:** Integration with the IGDB API allows access to extensive game data.

I chose these features to provide users with a comprehensive gaming experience, allowing them to discover new games, keep track of their favorites, and engage with the community through ratings and reviews.

## Standard User Flow

1. **Homepage:** Users land on the homepage where they can see a list of popular games.
2. **Filter:** Users can filter games based on platforms and genres.
3. **Game Details:** Clicking on a game takes users to the game details page where they can see more information about the game and any available ratings and reviews.
4. **Rating:** Logged-in users can rate the game and see the average rating provided by other users.
5. **List Creation:** Logged-in users can create lists of their favorite games, add new games to existing lists, or remove games from lists.
6. **Profile:** Users can view their profile page to see their lists and activity.

## Technology Stack

-   **Backend:** Python with Flask framework
-   **Database:** PostgreSQL
-   **Frontend:** HTML, CSS, JavaScript with Jinja templating
-   **API Integration:** IGDB API for game data
-   **Additional Tools:** SQLAlchemy for database management, Flask Debug Toolbar for debugging, Flask-Bcrypt for password hashing

## Additional Notes

-   The project relies heavily on the IGDB API for fetching game data. Please refer to the IGDB API documentation for usage guidelines and best practices.
-   Ensure that the PostgreSQL database is properly configured and running to support user authentication and data storage.
-   The project includes unit tests to ensure the reliability and functionality of the application. Run tests regularly to maintain code quality.
-   Continuous updates and improvements are planned for the future to enhance user experience and add new features.

Feel free to reach out for any questions or feedback!

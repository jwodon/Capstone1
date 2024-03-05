$(document).ready(function () {
    // Fetch platforms and genres
    fetchPlatforms();
    fetchGenres();

    const ratingSlider = $('#ratingSlider');
    const ratingDisplay = $('#ratingDisplay'); // Assuming you have an element with id "ratingDisplay" in your HTML

    ratingSlider.on('input', function () {
        ratingDisplay.text(ratingSlider.val());
    });

    // Function to fetch platforms
    function fetchPlatforms() {
        fetch('/api/platforms')
            .then((response) => response.json())
            .then((platforms) => {
                platforms.forEach((platform) => {
                    $('#platform').append(`<option value="${platform.id}">${platform.name}</option>`);
                });
            });
    }

    // Function to fetch genres
    function fetchGenres() {
        fetch('/api/genres')
            .then((response) => response.json())
            .then((genres) => {
                genres.forEach((genre) => {
                    $('#genre').append(`<option value="${genre.id}">${genre.name}</option>`);
                });
            });
    }

    // Function to fetch and populate games based on selected platform and genre
    function fetchAndPopulateGames(filters) {
        $('#gameList').html('<p>Loading games...</p>');

        let apiUrl = '/api/games';
        if (filters) {
            apiUrl += `?${filters}`;
        }

        fetch(apiUrl)
            .then((response) => response.json())
            .then((games) => {
                $('#gameList').empty(); // Clear the existing content
                if (games.length === 0) {
                    // Handle no results
                    $('#gameList').html('<p>No games found matching your filters.</p>');
                    return;
                }
                games.forEach((game) => {
                    // Create HTML for game card
                    const cardHtml = `
                    <div class="col-md-3">
                    <div class="card" style="width: 18rem;">
                      <img src="${game.cover_url || '/static/images/alt_cover_img.jpg'}" class="card-img-top" alt="${
                        game.name
                    }">
                      <div class="card-body">
                        <h5 class="card-title">${game.name}</h5>
                      </div>
                      <ul class="list-group list-group-flush">
                        <li class="list-group-item"><b>Genres:</b> ${game.genres.join(', ')}</li>
                        <li class="list-group-item"><b>Platforms:</b> ${game.platforms.join(', ')}</li>
                        <li class="list-group-item">
                          <b>Critic Rating:</b> ${
                              game.aggregated_rating ? game.aggregated_rating.toFixed(1) : 'Not Yet Available'
                          } (${game.aggregated_rating_count || 0} reviews)
                        </li>
                        <li class="list-group-item"><b>Community Rating:</b> ${
                            game.avg_rating || 'Not Yet Available'
                        }</li>
                      </ul>
                      <div class="card-body">
                        <a href="/games/${game.id}" class="card-link">Details</a>
                      </div>
                    </div>
                  </div>
                `;
                    $('#gameList').append(cardHtml);
                });
            })
            .catch((error) => {
                console.error('Error fetching games:', error);
                $('#gameList').html('<p class="error-message">Error fetching games. Please try again.</p>');
            });
    }

    // Event listeners for filters
    $('#filterForm').on('submit', function (event) {
        event.preventDefault();

        const platformId = $('#platform').val();
        const genreId = $('#genre').val();

        let queryString = '';
        if (platformId) {
            queryString += `platform=${platformId}`;
        }
        if (genreId) {
            if (queryString) {
                queryString += '&';
            }
            queryString += `genre=${genreId}`;
        }

        fetchAndPopulateGames(queryString);
    });
});

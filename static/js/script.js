$(document).ready(function () {
    // 1. Fetch platforms and genres
    fetchPlatforms();
    fetchGenres();

    // 3. Fetch games when filters change
    // $('#platform, #genre').on('change', function () {
    //     fetchGames();
    // });

    const ratingSlider = $('#ratingSlider');
    const ratingDisplay = $('#ratingDisplay'); // Add an element for display (see HTML snippet below)

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

    // Function to fetch genres (similar to fetchPlatforms)
    function fetchGenres() {
        fetch('/api/genres')
            .then((response) => response.json())
            .then((genres) => {
                genres.forEach((genre) => {
                    $('#genre').append(`<option value="${genre.id}">${genre.name}</option>`);
                });
            });
    }
});

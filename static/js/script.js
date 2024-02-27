$(document).ready(function () {
    // 1. Fetch platforms and genres
    fetchPlatforms();
    fetchGenres();
    fetchAndPopulateGames();

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

    // Function to fetch and populate the games dropdown
    // function fetchAndPopulateGames() {
    //     $('#game-select').prop('disabled', true).append(`<option value="" disabled selected>Loading games...</option>`);

    //     fetch('/api/games/all')
    //         .then((response) => response.json())
    //         .then((games) => {
    //             // Clear placeholder option
    //             $('#game-select option[value=""][disabled]').remove();

    //             // Populate the dropdown with game options
    //             games.forEach((game) => {
    //                 $('#game-select').append(`<option value="${game.id}">${game.name}</option>`);
    //             });
    //         })
    //         .finally(() => {
    //             // Re-enable the dropdown after loading completes
    //             $('#game-select').prop('disabled', false);
    //         });
    // }
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.like-comment').forEach(button => {
        button.addEventListener('click', function (event) {
            event.preventDefault(); // Prevent default form submission
            const commentId = this.dataset.commentId; // Get the comment ID

            fetch(`/comment/${commentId}/like/`, { // Send request to the backend
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'), // Ensure this function is defined and working
                },
            })
            .then(response => response.json())
            .then(data => {
                const likesCountSpan = this.querySelector('.likes-count'); // Get the likes count span
                likesCountSpan.textContent = data.new_like_count; // Update likes count
                this.classList.toggle('liked'); // Optionally change the button appearance
            })
            .catch(error => {
                console.error('Error:', error); // Log any errors
            });
        });
    });
});

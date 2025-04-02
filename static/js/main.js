$(document).ready(function() {
    // File upload name display
    $('#question_image').change(function() {
        const fileName = $(this).val().split('\\').pop();
        if (fileName) {
            $('#file-name').text('Selected file: ' + fileName);
        } else {
            $('#file-name').text('');
        }
    });
    
    // Form submission handling
    $('#mathForm').submit(function(e) {
        e.preventDefault();
        
        // Clear previous errors
        $('#error-message').addClass('hidden').text('');
        
        // Get form data
        const formData = new FormData(this);
        const hasText = formData.get('question_text').trim() !== '';
        const hasFile = formData.get('question_image').name !== '';
        
        // Validate input
        if (!hasText && !hasFile) {
            $('#error-message').removeClass('hidden').text('Please enter a question or upload an image');
            return;
        }
        
        // Show loading spinner
        $('#mathForm').addClass('hidden');
        $('#loading').removeClass('hidden');
        
        // Send AJAX request
        $.ajax({
            url: '/solve',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.error) {
                    // Show error message
                    $('#error-message').removeClass('hidden').text(response.error);
                    $('#mathForm').removeClass('hidden');
                    $('#loading').addClass('hidden');
                } else {
                    // Redirect to results page
                    window.location.href = '/result?problem=' + encodeURIComponent(response.problem_statement) + 
                                           '&solution=' + encodeURIComponent(response.solution_steps);
                }
            },
            error: function(xhr, status, error) {
                // Handle error
                $('#error-message').removeClass('hidden').text('An error occurred: ' + error);
                $('#mathForm').removeClass('hidden');
                $('#loading').addClass('hidden');
            }
        });
    });
});
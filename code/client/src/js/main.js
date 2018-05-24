console.log('here')
let state = '';
const serverURI = 'http://localhost:5555'

function getLoginState(){
    

    fetch('http://localhost:5555/login')
        .then( (response) => {
            if ( response.status !== 200 ) {
                console.log('check if the server is running, ' + response.status)
                return
            }
            response.json().then( ( data ) => {
                state = data.state;
                console.log(state);
            })
        })
}

function signInCallback(authResult) {
    if (authResult['code']) {
        // Hide the sign-in button now that the user is authorized
        $('#signinButton').attr('style', 'display: none');
        console.log(authResult)
        // Send the one-time-use code to the server, if the server responds, write a 'login successful' message to the web page and then redirect back to the main restaurants page
        $.ajax({
        type: 'POST',
        url: serverURI + '/gconnect?state='+ state,
        processData: false,
        data: JSON.stringify(authResult['code']),
        contentType: 'application/json',
        success: function(result) {
            // Handle or verify the server response if necessary.
            console.log('sucess')
            console.log(result)
            if (result) {
            $('#result').html('Login Successful!</br>'+ result + '</br>Redirecting...')
            setTimeout(function() {
            window.location.href = "/restaurant";
            }, 4000);
            
        } else if (authResult['error']) {
        console.log('There was an error: ' + authResult['error']);
    } else {
            $('#result').html('Failed to make a server-side call. Check your configuration and console.');
            }
        }
        
    }); } }



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
    const access_token = authResult.access_token;
    const data = {state, code: authResult['code']}
    console.log(JSON.stringify(data))
    
    console.log('before: ', JSON.stringify(data))
    fetch("http://localhost:5555/login", {
        method: 'POST',
        
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'appication/json'
        },
        body: JSON.stringify(data),
        cache: 'no-cache',
    })
    .then( ( response ) => {
        return response.json()
    }).then( ( data ) => {
        console.log(data)
    })
}
    var test_data = {name: 'Ahmed', age: 30}

    function testRequest() {
        fetch('http://localhost:5555/test', {
            method: 'POST',
            headers: {
                'content-type': 'appication/json'
            },
            body: JSON.stringify(test_data),
            cache: 'no-cache',
        }).then( ( response ) => {
            if (response.status !== 201 ) {
                console.log('Looks like the backend server is not running on port 5000. ' + response.status);
                response.json().then( ( data ) => {
                    console.log(data)
                })
                return false;
            }
            response.json().then( ( data ) => {
                console.log(data)
                return true;
            })
        })
    }

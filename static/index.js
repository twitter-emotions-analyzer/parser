document.getElementById("load-button").addEventListener("click", function(){
    const username = document.getElementById("username-input").value;
    console.log("clicked")
    fetch('http://localhost:5000/findTweets/' + username)
    .then(response => response.json())
    .then(tweets => {
        table = document.getElementById("table");
        tweets.forEach(tweet => {
            console.log(tweet)
            tr = document.createElement('tr')
            tdUsername = document.createElement('td')
            tdUsername.innerText = tweet.username
            
            tdText = document.createElement('td')
            tdText.innerText = tweet.tweet

            tdEmotion = document.createElement('td')
            tdEmotion.innerText = tweet.emotion
            tr.appendChild(tdUsername)
            tr.appendChild(tdText)
            tr.appendChild(tdEmotion)
            table.appendChild(tr)
        });
    })
  });
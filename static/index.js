document.getElementById("load-button").addEventListener("click", function(){
    const username = document.getElementById("username-input").value;
    console.log("clicked")
    fetch('http://ec2-18-191-230-61.us-east-2.compute.amazonaws.com:5000/findTweets/' + username)
	.then(response => response.json())
    .then(tweetsAndRates => {
        table = document.getElementById("table");
        tweetsAndRates.tweets.forEach(tweet => {
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
	chartData = tweetsAndRates.userRates.map((value, index) => {
		return {
			x: value.userRate,
			y: value.tweetsCount,
			name: value.username
		}
	});
	drawChart(chartData);
    })
  });
//drawChart([{x:0, y:0}]);

function drawChart(chartData) {
	var ctx = document.getElementById("chart").getContext("2d");
	var chart = new Chart(ctx, {
		type: 'scatter',
	    data: {
	        datasets: [{
	            backgroundColor: 'red',
	            data: chartData
	        }],
	    },
	    options: {
		legend: {
			display: false,
		},
		tooltips: {
			enabled: true,
			mode: 'single',
			callbacks: {
				label: function(tooltipItem, data) {
					console.log(data);
					return data.datasets[0].data[tooltipItem.index].name;
				}
			}
		},
		responsive: false,
		maintainAspectRatio: false,
	        scales: {
	            xAxes: [{
			scaleLabel: {
				display: true,
				labelString: "Emotion rate",
			},
	                type: 'linear',
	                position: 'bottom',
			ticks: {
				suggestedMin: 4,
				suggestedMax: -4
			}
	            }],
		    yAxes: [{
			scaleLabel: {
				display: true,
				labelString: "Tweets amount",
			}
		    }]
	        }
	    }
	});
}

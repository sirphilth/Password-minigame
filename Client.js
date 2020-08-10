// Start ws connection after document is loaded
$(document).ready(function() {

  // Connect if API_Key is inserted
  // Else show an error on the overlay
  if (typeof API_Key === "undefined") {
    $("body").html("No API Key found or load!<br>Rightclick on the script in ChatBot and select \"Insert API Key\"");
    $("body").css({"font-size": "20px", "color": "#ff8080", "text-align": "center"});
  }
  else {
    connectWebsocket();
  }

});

// Connect to ChatBot websocket
// Automatically tries to reconnect on
// disconnection by recalling this method
function connectWebsocket() {

  //-------------------------------------------
  //  Create WebSocket
  //-------------------------------------------
  var socket = new WebSocket("ws://127.0.0.1:3337/streamlabs");

  //-------------------------------------------
  //  Websocket Event: OnOpen
  //-------------------------------------------
  socket.onopen = function() {

    // AnkhBot Authentication Information
    var auth = {
      author: "SirPhilthyOwl",
      website: "twitch.tv/SirPhilthyOwl",
      api_key: API_Key,
      events: [
        "EVENT_USERNAME"
      ]
    };

    // Send authentication data to ChatBot ws server
    socket.send(JSON.stringify(auth));
  };

  //-------------------------------------------
  //  Websocket Event: OnMessage
  //-------------------------------------------
  socket.onmessage = function (message) {

    // Parse message
    var socketMessage = JSON.parse(message.data);
    console.log(socketMessage);

    // EVENT_USERNAME
    if (socketMessage.event == "EVENT_USERNAME") {
      var eventData = JSON.parse(socketMessage.data);
      var outroVar
      Intro(eventData);
    }
      if (eventData.mode == "NoUsers") {
        outroVar = setTimeout(outroTransition, 3000);
      }
      else if (eventData.mode == "Start") {
        Start(eventData);
      }
      else if (eventData.mode == "End") {
        End(eventData);
      }
      else if (eventData.mode == "Win") {
        Win(eventData);
      }
      else if (eventData.mode == "Leaderboard") {
        Leaderboard(eventData, outroVar);
      }
    }

  function Intro(eventData) {
    $("#alert").queue(function() {
      $(this).removeClass(settings.OutTransition + "Out initialHide");
      $("#alert").addClass(settings.InTransition + "In");
      if (eventData.mode == "None") {
        $("#encrypt").html("Password Mini-game");
      }
      $("#guess1").html(eventData.Guess1)
      $("#guess2").html(eventData.Guess2)
      $("#guess3").html(eventData.Guess3)
      $("#guess4").html(eventData.Guess4)
      $("#guess5").html(eventData.Guess5)
      document.getElementById('encrypt').style.color = settings.TextColor
      $("#logo").attr("src", "LockWhite.png");
      $(this).dequeue();
    });
  }

  function Start(eventData) {
    $("#alert").queue(function() {
      $("#encrypt").stringChange(eventData.Encrypt, "encrypt");
      changeGuess(eventData);
      $(this).dequeue();
    });
  }

  function End(eventData) {
    $("#alert").queue(function() {
     changeGuess(eventData);
     $("#encrypt").stringChange("The lock won't budge, better luck next time!", "encrypt")
     outroVar = setTimeout(outroTransition, 2000);
     $(this).dequeue();
   });
  }

  function Win(eventData) {
    $("#alert").queue(function() {
      changeGuess(eventData);
      $("#logo").changePicture("LockOpenWhite.png");
      $("#encrypt").stringChange("The password has been cracked!", "encrypt");
      outroVar = setTimeout(outroTransition, 2000);
      $(this).dequeue();
    });
  }

  function Leaderboard(eventData, outroVar) {
    $("#alert").queue(function() {
      if (outroVar != null) {
        clearTimeout(outroVar);
        $("#encrypt").fadeOut(function() {
          $("#encrypt").text("Leaderboard:");
        }).fadeIn();
      }
      if ($('#logo').attr('src') == "LockOpenWhite.png") {
          $("#encrypt").fadeOut(function() {
            $("#encrypt").text("Leaderboard:");
          }).fadeIn();
      }
      $("#encrypt").html("Leaderboard:");
      changeGuess(eventData);
      outroVar = setTimeout(outroTransition, 9000);
      $(this).dequeue();
    });
  }

  function changeGuess(eventData) {
    var obj = {
      "guess1": eventData.Guess1,
      "guess2": eventData.Guess2,
      "guess3": eventData.Guess3,
      "guess4": eventData.Guess4,
      "guess5": eventData.Guess5
    };
    $.each(obj, function(key, value) {
      $("#" + key).fadeOut(function() {
        $("#" + key).text(value.String);
      }).fadeIn();
      if (value.Color == "Positional") {
        document.getElementById(key).style.color = settings.PositionalColor;
      } else {
        document.getElementById(key).style.color = settings.GuessColor;
        }
    });
  }

  $.fn.stringChange = function(text, div) {
    document.getElementById(div).style.color = settings.TextColor;
    $(this).fadeOut(function() {
      $(this).text(text);
    }).fadeIn();
  }

  $.fn.changePicture = function(picture) {
    $(this).fadeOut(function() {
      $(this).attr("src", picture);
    }).fadeIn();
  }

  function outroTransition() {
    var tempVal
    $("#guess5").fadeOut();
    $("#guess4").fadeOut();
    $("#guess3").fadeOut();
    $("#guess2").fadeOut();
    $("#guess1").fadeOut();
    if ($("#encrypt").text() != "Password Mini-game") {
      $("#encrypt").stringChange("Password Mini-game", "encrypt");
    }
    setTimeout(function() {
      $("#alert").addClass(settings.OutTransition + "Out");
      $("#alert").removeClass(settings.InTransition + "In");
    },1000);
  }

  function stopOutro(outroVar) {
    if (outroVar != False) {
      clearInterval(outroVar);
    }
  }

    //-------------------------------------------
  //  Websocket Event: OnError
  //-------------------------------------------
  socket.onerror = function(error) {
    console.log("Error: " + error);
  }

  //-------------------------------------------
  //  Websocket Event: OnClose
  //-------------------------------------------
  socket.onclose = function() {
    // Clear socket to avoid multiple ws objects and EventHandlings
    socket = null;
    // Try to reconnect every 5s
    setTimeout(function(){connectWebsocket()}, 5000);
  }

};

var app = angular.module('App',[]);

// Change angular html template tags to avoid conflict with flask
app.config(function($interpolateProvider) {
  $interpolateProvider.startSymbol('[[');
  $interpolateProvider.endSymbol(']]');
});

app.controller('Ctrl', function($scope, socket) {


    // scoket listenters
    socket.on('status', function (data) {
        // application logic ....
        $scope.status = data.msg;
    });

    // scoket listenters
    socket.on('push', function (data) {
        // application logic ....
        d = JSON.parse(data);
        // d = data;

        var a = d.BMP.split("B");
        $scope.data = a[1];
        // $scope.data.avePre
        console.log(a[1]);
    });

    $scope.count = function(){
        socket.emit('count');
        return false;
    }
    $scope.clear = function(){
        socket.emit('clear');
        return false;
    }
    $scope.tempToColor = function(temp){
      if (temp<26) {
        return "bg-info";
      } else if (temp > 26 && temp < 29) {
        return "bg-warning";
      } else {
        return "bg-danger";
      }
    }

    // Pulsean
    var canvPulse = document.getElementById("canvPulse");
    canvPulse.setAttribute("width", 350);
    canvPulse.setAttribute("height", 200);
    // canv.setAttribute("style", "margin: 0 10px");
    var smoothiePulse = new SmoothieChart({
      grid: { strokeStyle:'green', fillStyle:'black',
              lineWidth: 1, millisPerLine: 1000, verticalSections: 5, },
      labels: { fillStyle:'white', fontSize:24 },
      maxValue:200,
      minValue: 0
    });
    // Data
    var linePulse = new TimeSeries();

    // Add a random value to each line every second
    setInterval(function() {
      linePulse.append(new Date().getTime(), $scope.data);
      // line2.append(new Date().getTime(), Math.random());
    }, 500);

    // Add to SmoothieChart
    smoothiePulse.addTimeSeries(linePulse,{
      lineWidth:4,
      strokeStyle:'rgb(248,248,248)',
      fillStyle:'rgba(248,248,248,0.30)',
      lineWidth:3
    });

    smoothiePulse.streamTo(canvPulse, 100);

//
});


app.factory('socket', function ($rootScope) {
  var socket = io.connect('http://' + document.domain + ':' + location.port + '/main');
  return {
    on: function (eventName, callback) {
      socket.on(eventName, function () {
        var args = arguments;
        $rootScope.$apply(function () {
          callback.apply(socket, args);
        });
      });
    },
    emit: function (eventName, data, callback) {
      socket.emit(eventName, data, function () {
        var args = arguments;
        $rootScope.$apply(function () {
          if (callback) {
            callback.apply(socket, args);
          }
        });
      })
    }
  };
});


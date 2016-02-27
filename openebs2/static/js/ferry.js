var ferryApp = angular.module('ferryApp', ['ngResource']);
var baseUrl = "http://127.0.0.1:8000"
ferryApp.controller('TripListCtrl', ['$scope', 'tripService', function ($scope, tripService) {
    var ctrl = this;
    $scope.trips = [];
    $scope.selected = 0;
    ctrl.select = function(trip) {
        if ( $scope.selected != trip) {
            $scope.selected = trip;
        } else {
            $scope.selected = null;
        }
    }
    ctrl.getTrips = function() {
        tripService.getTrips(362, function(data) {
            $scope.trips = data;
        })
    }
    ctrl.getTrips();

}]);

//ferryApp.controller('FormCtrl', ['$scope', function($scope) {
//    $scope.on('trip-selected', function(args) {
//        $scope.selected = args.trip;
//    });
//}]);

ferryApp.service('tripService', ['$resource', function($resource) {
    var blockResource = $resource(baseUrl+"/ferry/:id/trips.json");
    this.getTrips = function(line, callback) {
        return blockResource.get({ id: line }).$promise.then(function(data) {
            callback(data.object);
        });
    }
}]);

ferryApp.filter('formatTime', function() {
    return function(time) {
        seconds = parseInt(time);
        var hours   = Math.floor(seconds / 3600);
        var minutes = Math.floor((seconds - (hours * 3600)) / 60);
        var extra = "";
        if (hours > 23) {
            hours = hours - 24
            extra = " <em>(+1)</em>"
        }
        return ""+padTime(hours)+":"+padTime(minutes)+extra;
    }
});


function padTime(i) {
    str = i.toString()
    if (str.length == 2) {
        return str;
    } else if (str.length == 1) {
        return '0'+str;
    } else {
        return '00';
    }
}
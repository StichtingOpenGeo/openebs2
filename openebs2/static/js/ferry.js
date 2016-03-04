var ferryApp = angular.module('ferryApp', ['ngResource', 'ui.bootstrap']);
var baseUrl = "http://127.0.0.1:8000"
ferryApp.controller('TripListCtrl', ['$scope', '$uibModal', 'tripService', function ($scope, $uibModal, tripService) {
    var ctrl = this;
    $scope.trips = [];
    $scope.selected = null;
    ctrl.select = function(trip) {
        if ( $scope.selected != trip) {
            $scope.selected = trip;
        } else {
            $scope.selected = null;
        }
    }
    $scope.openDelay = function () {
        $uibModal.open({
            animation: true,
            templateUrl: 'modal_delay.html',
            controller: 'DelayModalCtrl',
            resolve: {
                selected: function () { return $scope.selected; }
            }
        });
    };

    $scope.openSuspend = function () {
        $uibModal.open({
            animation: true,
            templateUrl: 'modal_suspend.html',
            controller: 'SuspendModalCtrl',
            resolve: {
                selected: function () { return $scope.selected; }
            }
        });
    };

    $scope.$watch("ferry", function(oldVal, newVal) {
        console.log("Changed to "+newVal);
        if (newVal !== oldVal) {
            ctrl.getTrips();
        }
    });
    ctrl.getTrips = function() {
        tripService.getTrips($scope.ferry, function(data) {
            $scope.trips = data;
        })
    }
    ctrl.getTrips();
}]);


ferryApp.controller('DelayModalCtrl', function($scope, selected) {
    $scope.selected = selected;
});

ferryApp.controller('SuspendModalCtrl', function($scope, selected) {
    $scope.selected = selected;
});
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
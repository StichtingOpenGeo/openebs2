var ferryApp = angular.module('ferryApp', ['ngResource', 'ngCookies', 'ui.bootstrap']);
/*var baseUrl = "http://127.0.0.1:8000"*/
var baseUrl = window.location.protocol + "//" + window.location.hostname + (window.location.port ? ':' + window.location.port: '')
ferryApp.controller('TripListCtrl', ['$scope', '$cookies', '$uibModal', 'tripService',
        function ($scope, $cookies, $uibModal, tripService) {

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
                ferry: function() { return $scope.ferry; },
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
                ferry: function() { return $scope.ferry; },
                selected: function () { return $scope.selected; }
            }
        });
    };
    ctrl.restoreFerry = function() {
        val = $cookies.get("openebs_ferry");
        if (val == null) {
            val = $("#selectFerry option:first").val();
        }
        return val;
    }
    $scope.$watch("ferry", function(newVal, oldVal) {
        ctrl.getTrips(newVal);
        $cookies.put("openebs_ferry", newVal)
    });
    ctrl.getTrips = function(ferry_line) {
        if (ferry_line == null) {
            return;
        }
        tripService.getTrips(ferry_line, function(data) {
            $scope.trips = data;
        })
    }
    ctrl.getTrips($scope.ferry);
}]);


ferryApp.controller('DelayModalCtrl', function($scope, ferry, selected) {
    $scope.ferry = ferry;
    $scope.selected = selected;
});

ferryApp.controller('SuspendModalCtrl', function($scope, ferry, selected) {
    $scope.ferry = ferry;
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
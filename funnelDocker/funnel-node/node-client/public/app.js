var angular = require('angular')
var angular_route = require('angular-route')
var ngtable = require('ng-table')
var mdl = require('material-design-lite')
var hljs = require ('angular-highlightjs')
var markdown = require ('angular-markdown-directive')
var app = angular.module('TESApp', ['ngRoute', 'ngTable', 'hljs']);


function shortID(longID) {
  return longID.split('-')[0];
}
var jobSelected = '';
var workerSelected = {};

app.controller('TaskBoxController', function($scope, $parse, $http) {
  
    $scope.editObject = '{"name": "Date loop","projectId": "TES development","description": "Print the date every second, for-ev-or.","inputs": [],"outputs": [],"resources": {},"executors": [{"image_name": "alpine","cmd": ["sh", "-c", "while true; do date; sleep 1; done"],"stdout": "/tmp/stdout","stderr": "/tmp/stderr"}]}';
    
    $scope.prettyJSON = '';
    
    $scope.tabWidth = 4;
    
    var _lastGoodResult = '';
    $scope.toPrettyJSON = function (objStr, tabWidth) {
      try {
        var obj = $parse(objStr)({});
      }catch(e){
        // eat $parse error
        return _lastGoodResult;
      }
      
      var result = JSON.stringify(obj, null, Number(tabWidth));
      _lastGoodResult = result;
      
      return result;
    };

    // task submittion
  $scope.submitTask = function(data) {
    // $http.post('/newTask',msg );
    $http.post('/newTask',$scope.editObject).
        success(function(data) {
            console.log("posted successfully");
        }).error(function(data) {
            console.error("error in posting");
        })    
  };    
  
});


app.controller('JobListController', function($scope, NgTableParams, $http) {
  $scope.url = "/jobList";
  $scope.shortID = shortID;
  $scope.click = function(jobid) {
    jobSelected = jobid;
  };
  $scope.fetchJobs = function () {
    $http.post($scope.url).then(function(result) {
      var jobs = result.data.jobs || [];
      $scope.tableParams = new NgTableParams(
        {
          count: 25
        }, 
        {
          counts: [25, 50, 100],
          paginationMinBlocks: 2,
          paginationMaxBlocks: 10,
          total: jobs.length,
          dataset: jobs
        }
      );
    });
  }

  $scope.fetchJobs ();

  $scope.cancelJob = function(jobid) {
    var data = { jobID : jobid}
    $http.post("/deleteJob", JSON.stringify(data));
    $scope.fetchJobs ();
  }
});

app.controller('JobInfoController', function($scope, $http, $routeParams) {
  $scope.job = {};
  $scope.cmdStr = function(cmd) {
    return cmd.join(' ');
  };

  $scope.fetchContent = function() {
    var data = { jobID : jobSelected}
    console.log (data);
    $http.post('/job', JSON.stringify(data)).then(function(result){
      console.log(result.data);
      $scope.job = result.data
    })
  }
  $scope.fetchContent();

  $scope.cancelJob = function() {
    var data = { jobID : jobSelected}
    $http.post("/deleteJob", JSON.stringify(data));
    $scope.fetchContent();
  }
});


app.controller('WorkerListController', function($scope, $http) {
	$scope.url = "/workerList";
	$scope.workers = [];
  $scope.click = function(worker) {
    workerSelected = worker;
    console.log (workerSelected);
  };

  $http.post($scope.url).then(function(result) {
    var workers = result.data.workers || [];
    console.log(workers)
    $scope.workers = workers;
  });
});

app.controller('WorkerInfoController', function($scope, $http) {
	$scope.url = "/workerList";
	$scope.worker = workerSelected;

});

app.config(
  ['$routeProvider',
   function($routeProvider) {
     $routeProvider
     .when('/', {
       templateUrl: 'taskView'
     })
     .when('/taskbox/', {
       templateUrl: 'taskView'
     })
     .when('/jobs/', {
       templateUrl: 'jobListView',
     }).
     when('/jobinfo', {
       templateUrl: 'jobInfoView'
     }).
     when('/workers/', {
       templateUrl: 'workerListView'
     }).
     when('/workerinfo/', {
       templateUrl: 'workerInfoView'
     })
   }
  ]
);

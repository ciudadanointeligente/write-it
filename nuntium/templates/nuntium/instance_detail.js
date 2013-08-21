console.log("muchas gracias a los cabros de epistemonikos.org por la ayuda con angularjs")


var app = angular.module('writeit', []);
angular.module('writeit').config(function($interpolateProvider) {
  $interpolateProvider.startSymbol('[[');
  $interpolateProvider.endSymbol(']]');
});
app.controller('message-form',function($scope, $http, $filter, $log){
	$scope.persons = 
		[{% for person in writeitinstance.persons.all %}
		{
			"name": "{{ person }}",
			"id":{{ person.id }}
		}
		{% if not forloop.last %}
		{# just in case there are still some ie6 around #}
			,
		{% endif %}
		{% endfor %}
		];

		$scope.comp = function(person){
			var text = $scope.searchTerm;
			if($scope.searchTerm == undefined){
				return true;
			}
			var text = $scope.searchTerm
			text = removeDiacritics((''+text).toLowerCase());
			var name = removeDiacritics(('' + person.name).toLowerCase())
          	return name.indexOf(text) > -1
		};
	});
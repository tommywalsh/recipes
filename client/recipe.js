
/**
 * Standalone view model class representing a single step in a recipe.
 *
 * It contains these fields...
 *  - ingredients: An observable array of observable objects, each having a single property called 'text'
 *  - instructions: An observable string object
 *  - duration: An observable string object telling how many hours/minutes this step takes
 *
 * ... and these methods:
 *  - addIngredient: Adds one new item (with an empty 'text' field) to the ingredients list.
 *  - removeIngredient: Removes the ingredient with the given index from the list.
 *  - toJson: Returns a non-observable copy of the data, in the same format as the server expects.
 */
var RecipeStepViewModel = function(ingredients, instructions, duration) {
    var self = this

    self.ingredients = ko.observableArray()
    for (var i = 0; i < ingredients.length; i++) {
        self.ingredients.push(ko.observable({
            text: ingredients[i]
        }))
    }
    self.instructions = ko.observable(instructions)
    self.duration = ko.observable(duration)

    self.addIngredient = function() {
        self.ingredients.push(ko.observable({
            text: ""
        }))
    }.bind(self)

    self.removeIngredient = function(index) {
        self.ingredients.splice(index, 1)
    }

    self.toJson = function() {
        var ingredientsJson = []
        var ingredientsArray = self.ingredients()
        for (var i = 0; i < ingredientsArray.length; i++) {
            ingredientsJson.push(ingredientsArray[i]().text)
        }

        return {
            ingredients: ingredientsJson,
            instructions: self.instructions(),
            duration: toMinutes(self.duration())
        }
    }
}

/**
 * View model class representing an entire recipe.
 *
 * It contains these fields...
 *  - title: an observable string
 *  - description: an observable string
 *  - tags: an observable array of strings
 *  - steps: an observable array of RecipeStepViewModels
 */
var RecipeViewModel = function(recipeId) {
    var self = this
    self.title = ko.observable()
    self.description = ko.observable()
    self.tags = ko.observableArray()
    self.steps = ko.observableArray()

    self.acceptData = function(recipeJson) {
        self.title(recipeJson.title)
        self.description(recipeJson.description)
        self.tags(recipeJson.tags)
        self.steps([])
        for (var i = 0; i < recipeJson.steps.length; i++) {
            self.steps.push(new RecipeStepViewModel(
                recipeJson.steps[i].ingredients,
                recipeJson.steps[i].instructions,
                fromMinutes(recipeJson.steps[i].duration)
            ))
        }
    }

    self.requestData = function(recipeId) {
        let filename = `${recipeId}.json`
        fetch(filename)
          .then(response => response.json())
          .then(json => self.acceptData(json))
    }

    self.requestData(recipeId)
}


/**
 * Alternate version of the recipe view models that are useful for using at cooking time.
 */
var RecipeStepCookTimeViewModel = function(ingredients, other_inputs, instructions) {
    var self = this

    self.ingredients = ko.observableArray()
    for (var i = 0; i < ingredients.length; i++) {
        self.ingredients.push(ko.observable({
            text: ingredients[i]
        }))
    }

    self.other_inputs = ko.observableArray()
    for (var i = 0; i < other_inputs.length; i++) {
        self.other_inputs.push(ko.observable({
            text: other_inputs[i]
        }))
    }

    self.instructions = ko.observable(instructions)
    self.isCompleted = ko.observable(false)
}

var RecipeCookTimeViewModel = function(recipeId) {
    var self = this
    self.title = ko.observable()
    self.steps = ko.observableArray()
    self.startTime = ko.observable(0)

    self.acceptData = function(recipeJson) {
        self.title(recipeJson.title)
        self.steps([])
        var previousStopTime = self.startTime
        for (var i = 0; i < recipeJson.steps.length; i++) {
            var model = new RecipeStepCookTimeViewModel(
                recipeJson.steps[i].ingredients,
                recipeJson.steps[i].other_inputs,
                recipeJson.steps[i].instructions
            )
            self.steps.push(model)
            previousStopTime = model.completionTime
        }
    }

    self.requestData = function(recipeId) {
        let filename = `recipes/${recipeId}.json`
        fetch(filename)
          .then(response => response.json())
          .then(json => self.acceptData(json))
    }

    self.requestData(recipeId)
}


var RecipeListViewModel = function(recipeId) {
    var self = this
    self.recipes = ko.observableArray()

    self.acceptData = function(recipeJson) {
        self.recipes(recipeJson)
    }

    self.requestData = function(recipeId) {
        let filename = `recipe_list.json`
        fetch(filename)
          .then(response => response.json())
          .then(json => self.acceptData(json))
    }

    self.requestData(recipeId)
}

function runAjax(url, method, data) {
    var request = {
      url: url,
      type: method,
      contentType: "application/json",
      accepts: "application/json",
      cache: false,
      dataType: 'json',
      data: JSON.stringify(data)
    }
    return $.ajax(request)
}

function getRecipeUrl(id) {
    url = "http://172.17.0.2/recipes/"
    if (id) {
        url += id
    }
    return url
}

function getUrlVars() {
    var vars = {}
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
        vars[key] = value
    })
    return vars
}

function getUrlParam(paramName) {
    var paramValue
    if (window.location.href.indexOf(paramName) > -1) {
        paramValue = getUrlVars()[paramName]
    }
    return paramValue
}

function getUrl(fcnName, id) {
    return fcnName + ".html?id=" + id
}

/**
 * Returns an integer number of minutes. Incoming string should be in HH:MM format (with the hours being optional)
 */
function toMinutes(timeSpec) {
    var hmSpec = /^((\d\d?):)?(\d\d?)$/
    var result = timeSpec.match(hmSpec)
    var hours = 0
    var minutes = 0
    if (result) {
        if (result[2]) {
            hours = parseInt(result[2])
        }
        minutes = parseInt(result[3])
    }
    return hours*60 + minutes
}

function fromMinutes(minutes) {
    var hours = Math.floor(minutes/60)
    var remainderMinutes = minutes - hours*60
    var minuteString = String(remainderMinutes)
    if (hours > 0) {
        return hours + ":" + minuteString.padStart(2, '0')
    } else {
        return String(remainderMinutes)
    }
}
/**
 * Closures are functions defined inside (enclosed by) other functions. They have access to the variables in their lexical
 * environments (the outer functions). Even when the outer functions have been removed from the execution stack, a reference
 * to the outer function's variables remains in memory.
 */

// Consider the closure 'print' inside the following function.
// Can you predict what it will log to the console for all 100 brochures?
function getCarBrochures(numBrochures) {

    var brochures = [];

    for (var i = 0; i < numBrochures; i++) {
        var brochureNumber = i;
        brochures.push({
            name: 'brochure ' + brochureNumber,
            print: function(){
                console.log('I am brochure ' + brochureNumber);
            }
        });
    }

    return brochures;
}

carBrochures = getCarBrochures(100);

// All the carBrochures print brochureNumber 99, which is the variable's value that
// has sticked around in memory and accessed when we now execute the code inside print().
console.log(carBrochures[0].name);
console.log(carBrochures[0].print());
console.log(carBrochures[1].name);
console.log(carBrochures[1].print());

// To prevent making this mistake,
// - use a block scoped variable, let brochureNumber = i on line 14, or
// - copy variable i at time of iteration by passing it as a paramater to a wrapper function:
//   print: (function(j){ return function() { console.log('I am a brochure ' + j); } })(brochureNumber)


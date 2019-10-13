/**
 * Although javascript doesn't have namespaces, we can fake them using objects as containers.
 *
 * This is useful for preventing conflicting variable or function names when using a lot of libraries in your code.
 * Wrapping code in a function is one implementation of this, as functions are just objects in javascript.
 */

// In this example the two $ variables are conceptually in the same namespace and are properties of the global object.
// In case of a browser, the global object may be named 'window'. So only window.$ holding value 2 would persist.
var $ = 1;
console.log('a. ', $);

var $ = 2;
console.log('b. ', $);

// We can wrap each $ by its own object.
var myLib = {
    $: 3
};
var anotherLib = {
    $: 4
};
console.log('c. ', $);
console.log('d. ', myLib.$);
console.log('e. ', anotherLib.$);

// We can also wrap each $ variable by its own function object.
(function () {
    var $ = 5;
    console.log('f. ', $);
})();

console.log('g. ', $);
console.log('h. ', myLib.$);
console.log('i. ', anotherLib.$);
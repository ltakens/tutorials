/**
 * Before running your code, the javascript engine creates an execution context. Variables and functions along with their code are placed into memory.
 * This is referred to as hoisting.
 *
 * Variables and functions are declared and assigned the value undefined before code execution reaches the line where they are lexically declared.
 * When using function expressions as opposed to function statements, this can lead to unexpected results. Also, for people coming from different programming
 * languages, e.g. Python, this may be surprising.
 */

console.log('justAVariable was put into memory and assigned the value ', justAVariable);
console.log('justAFunction was put into memory: ', justAFunction);
console.log('justAFunction was put into memory and is invokable: ', justAFunction());
console.log('referenceToAnotherFunction was put into memory and assigned the value: ', anotherVariable);
console.log('referenceToAnotherFunction is not invokable until the = operator function finishes: ', anotherVariable());

// Variable hoisted before this line of code is run
var justAVariable = 1;

// Function hoisted before this line of code is run
function justAFunction() {
    return 2;
}

// Variable hoisted before this line of code is run
var anotherVariable = function () {
    return 3;
};
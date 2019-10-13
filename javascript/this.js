/**
 * When the execution context is created, the javascript engine creates a variable called 'this' in it and sets it
 * to refer to an object that will be regarded as the context.
 *
 * The actual object 'this' refers to may be surprising.
 */

// On the module level 'this' refers to the global object. In a browser this may be the Window object.
var someObj = {
    property: {
        embedded: {
            superEmbedded: this
        }
    }
};
function justAFunction() {
    return this;
}
console.log('a. ', this);
console.log('b. ', someObj.property.embedded.superEmbedded);
console.log('c. ', justAFunction());

// Inside a method of an object, the 'this' keyword is set to point to the object
var john = {
    firstName: 'John',
    lastName: 'Doe',
    getFullName: function () {
        return this.firstName + ' ' + this.lastName;
    }
};
console.log('d. ', john.getFullName());

// When using the 'new' operator to create an object from a constructor function,
// 'this' in the resulting object is pointing to the object itself.
// Note that if we just run Book() without the new operator, 'this' will refer to the global object and
// we will be setting window.name.
function Book() {
    this.name = 'book';
}
var book = new Book();
console.log('e. ', book.name);

// Inside a function inside a method, 'this' surprisingly refers to the global object
var mike = {
    firstName: 'Magic',
    lastName: 'Mike',
    printFullName: function () {
        function getFullName() {
            console.log('this refers to: ', this);
            return this.firstName + ' ' + this.lastName;
        }
        return 'Mr. ' + getFullName();
    }
};
console.log('f. ', mike.printFullName());

// In the previous example, we probably would want getFullName to have a reference to the mike object.
// We can do this by saving a reference to the outer function's 'this' variable.
var mike2 = {
    firstName: 'Magic',
    lastName: 'Mike',
    printFullName: function () {
        var self = this;
        function getFullName() {
            console.log('self refers to: ', self);
            return self.firstName + ' ' + self.lastName;
        }
        return 'Mr. ' + getFullName();
    }
};
console.log('g. ', mike2.printFullName());

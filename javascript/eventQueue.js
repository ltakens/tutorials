/**
 * When the execution stack is empty, the event queue is looked at by the javascript engine.
 * Then, for every function attached to an event, a new execution context is created and placed on the execution stack.
 * This means that functions that run for a long time before finishing, will hold up other events in the the event queue
 * to be handled.
 */

function clickHandler() {
    console.log('clickHandler invoked.');
}

function longRunningFunction() {
    console.log('longRunningFunction started.');
    var now = (new Date()).getTime();
    var later = now + 5 * 1000;
    while (now < later) {
        now = (new Date()).getTime();
    }
    console.log('longRunningFunction finished.');
}

document.addEventListener('click', clickHandler);
longRunningFunction();

// Paste the code into a browser javascript console and click inside the document a couple of times.
// What will be the order of the log messages in the console?

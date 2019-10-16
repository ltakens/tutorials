/**
 * In React the 'setState' function is the primary way to update a component's state and trigger
 * re-rendering of the component and its child components.
 */

/** Example 1: Updating a component's state based on the previous state. */
class MyComponent extends React.Component {

    constructor(props) {
        super(props);
        this.state = { myList: [1, 2, 3] };
    }

    handleSomeEvent = () => {
        const newElement = 4;
        // Do not use this.state.myList to update its value, because some other
        // state updates are pending and have not yet updated this.state.
        // Instead use an updater function that takes the previous state as an argument
        // that is guaranteed to be up to date, i.e. (prevState, props) => newState
        this.setState(prevState => ({ myList: [...prevState.myList, newElement] }));
    };

    render() {}
}

/** Example 2: Accessing the new state after updating it. */
class MyComponent extends React.Component {

    constructor(props) {
        super(props);
        this.state = { prop: 0 };
    }

    handleSomeEvent = () => {
        // Do not try access this.state directly after calling this.setState as your state
        // update is queued and possibly not yet executed.
        // Instead, pass in a callback function to setState to execute once your state update
        // is done (alternatively you can place your logic in the componentDidUpdate lifecycle method).
        this.setState({ prop: 1 }, () => console.log('I was updated:', this.state));
    };

    render() {}
}

/** Example 3: Updating nested objects in a component's state. */
class MyComponent extends React.Component {

    constructor(props) {
        super(props);
        this.state = { myObj: { parent: { child: { grandChild: null } } } };
    }

    handleSomeEvent = () => {
        // As setState does only shallow updates, we need to supply the entire new
        // value for the state property we want to update. In case we want to update the
        // grandchild property nested in our state's myObj, we need to supply
        // the entire new object.
        this.setState(prevState => {
            // prevState is a copy of the previous state object, so no worries about
            // modifying it.
            const newState = prevState;
            newState.myObj.parent.child.grandChild = 1;
            return newState;
        });
    };

    render() {}
}


import * as React from "react";
import * as ReactDOM from "react-dom";
import { BrowserRouter as Router, Route, Link, Redirect, Switch, useParams } from "react-router-dom";
import Gallery from "react-photo-gallery";

function getAppearanceUri(person) {
    if (person.defaultAppearanceId === null) {
        return "static/images/no-face.jpg";
    } else {
        return `/api/appearances/${person.defaultAppearanceId}/image`;
    }
}

function getDisplayName(person) {
    if (person.displayName) {
        return person.displayName;
    } else {
        return `${person.firstName} ${person.surname}`;
    }
}

function Header() {
    return (
        <div id="header">
            <Link to="/pictures">Pictures</Link>
            <Link to="/people">People</Link>
        </div>
    );
}

function GalleryPanel({day}) {
    const [pictures, setPictures] = React.useState([]);

    React.useEffect(() => {
        const abortController = new AbortController();

        fetch(`/api/pictures/for-day/${day}`, {signal: abortController.signal})
            .then(resp => {
                if (resp.ok) {
                    return resp.json();
                }
            })
            .then(json => {
                setPictures(json);
            });

        return function cleanup() {
            abortController.abort();
        };
    }, []);

    return <Gallery photos={pictures.map(id => {
        return {
            src: `/api/pictures/${id}`
        }
    })} />;
}

function GalleryList() {
    const [days, setDays] = React.useState({});

    React.useEffect(() => {
        const abortController = new AbortController();

        fetch("/api/pictures/count-per-day", {signal: abortController.signal})
            .then(resp => {
                if (resp.ok) {
                    return resp.json();
                }
            })
            .then(json => {
                setDays(json);
            });

        return function cleanup() {
            abortController.abort();
        };
    }, []);

    return (
        <div className="gallery-list">
            {Object.keys(days).map(day => {
                return <GalleryPanel key={day} day={day} />;
            })}
        </div>
    );
}

function PersonTile(person) {
    return (
        <a className="person-tile" href={`/people/${person.id}`}>
            <div className="circle-border">
                <img src={getAppearanceUri(person)} />
            </div>
            <div>{getDisplayName(person)}</div>
        </a>
    );
}

function People() {
    const [people, setPeople] = React.useState([]);

    React.useEffect(() => {
        const abortController = new AbortController();

        fetch("/api/people", {signal: abortController.signal})
            .then(resp => {
                if (resp.ok) {
                    return resp.json();
                }
            })
            .then(json => {
                setPeople(json);
            });

        return function cleanup() {
            abortController.abort();
        };
    }, []);

    return (
        <div className="people-list">
            {people.map(person => {
                return <PersonTile key={person.id} {...person} />;
            })}
        </div>
    );
}

function Person() {
    const abortController = new AbortController();

    const { id } = useParams();

    const [person, setPerson] = React.useState({
        firstName: "",
        middleNames: "",
        surname: "",
        displayName: "",
        defaultAppearanceId: null
    });

    function updatePerson(fields) {
        const newPerson = {...person, ...fields};

        fetch(`/api/people/${id}`,
              {
                  method: "POST",
                  headers: {
                    'Content-Type': 'application/json',
                  },
                  signal: abortController.signal,
                  body: JSON.stringify(newPerson)
              });

        setPerson(newPerson);
    }

    React.useEffect(() => {
        fetch(`/api/people/${id}`, {signal: abortController.signal})
            .then(resp => {
                if (resp.ok) {
                    return resp.json();
                }
            })
            .then(json => {
                setPerson(json);
            });

        return function cleanup() {
            abortController.abort();
        };
    }, []);

    return (
        <div className="person">
            <div className="circle-border">
                <img src={getAppearanceUri(person)} />
            </div>
            <div className="flex-column separate-children-small">
                <input className="display-name"
                       value={getDisplayName(person)}
                       onChange={e => updatePerson({displayName: e.target.value})}/>
                <div className="flex-row separate-children-small">
                    <label>
                        <span>First Name</span>
                        <input value={person.firstName}
                               onChange={e => updatePerson({firstName: e.target.value})} />
                    </label>
                    <label>
                        <span>Middle Names</span>
                        <input value={person.middleNames}
                               onChange={e => updatePerson({middleNames: e.target.value})} />
                    </label>
                    <label>
                        <span>Surname</span>
                        <input value={person.surname}
                               onChange={e => updatePerson({surname: e.target.value})}/>
                    </label>
                </div>
            </div>
        </div>
    );
}

function Content() {
    return (
        <div id="content">
            <Switch>
                <Route path="/pictures">
                    <GalleryList />
                </Route>
                <Route path="/people/:id">
                    <Person />
                </Route>
                <Route path="/people">
                    <People />
                </Route>
                <Route path="/">
                    <Redirect to="/pictures" />
                </Route>
            </Switch>
        </div>
    );
}

function App() {
    return (
        <Router>
            <Header />
            <Content />
        </Router>
    );
}

ReactDOM.render(<App/>, document.getElementById("root"));

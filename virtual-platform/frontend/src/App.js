import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';

// Import components
import Navbar from './components/Navbar';
import Home from './components/Home';
import Login from './components/Login';
import Register from './components/Register';
import Meetings from './components/Meetings';
import Concerts from './components/Concerts';
import Shopping from './components/Shopping';
import Art from './components/Art';
import Payments from './components/Payments';
import Enterprise from './components/Enterprise';
import Pathos from './components/Pathos';

// Import Tailwind CSS
import './index.css';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <Navbar />
        <div className="container mx-auto px-4 py-8">
          <Switch>
            <Route exact path="/" component={Home} />
            <Route path="/login" component={Login} />
            <Route path="/register" component={Register} />
            <Route path="/meetings" component={Meetings} />
            <Route path="/concerts" component={Concerts} />
            <Route path="/shopping" component={Shopping} />
            <Route path="/art" component={Art} />
            <Route path="/payments" component={Payments} />
            <Route path="/enterprise" component={Enterprise} />
            <Route path="/pathos" component={Pathos} />
          </Switch>
        </div>
      </div>
    </Router>
  );
}

export default App;

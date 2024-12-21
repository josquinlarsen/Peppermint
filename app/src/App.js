import React, { useState } from 'react';
import { Link, Routes, Route } from 'react-router-dom';
import './App.css';
import Login from "./components/Login";
import Logout from "./components/Logout";
import Register from './components/Register';
import User from './components/User';
import Welcome from './components/Welcome';

function App() {
    const [isLoggedIn, setIsLoggedIn] = useState(false);

    const handleLogout = () => {
        localStorage.removeItem('token');
        setIsLoggedIn(false);
    };

    return (
        <>
            <header>
                <div class="navbar">
                <div>
                    <h1>Peppermint</h1>
                </div>
                <div>
                    <nav>
                        {isLoggedIn ? (
                            <>
                            <Link to="/">Home</Link>
                            <Link to='/user'>Profile</Link>
                            <Link to='/logout'>Logout</Link>
                            </>
                        
                        ) : (
                            <>
                            <Link to="/">Home</Link>
                            <Link to="/register">Register</Link>
                            <Link to="/login">Login</Link>
                            </>
                        )}
                    </nav>
                </div>
                </div>
            </header>
            <main>
            <Routes>
                <Route path="/" element={<Welcome />} />
                <Route path='/register' element={<Register />} />
                <Route path="/login" element={<Login setIsLoggedIn={setIsLoggedIn} />} />
                <Route path="/user" element={<User />} /> 
                <Route path="/logout" element={<Logout setIsLoggedIn={setIsLoggedIn} />} />
                
            </Routes>
            </main>
            <footer>
                <p>&copy;2024</p>
            </footer>
        </>
    );
}

export default App;
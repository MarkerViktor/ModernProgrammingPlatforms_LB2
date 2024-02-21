import { useState, useContext, createContext, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'


export const Role = {
    GUEST: 'guest',
    ADMIN: 'admin',
    USER: 'user',
}

const defaultAuthContextData = {
    role: localStorage.getItem('role') || Role.GUEST,
    userId: localStorage.getItem('userId') || null,
}
const defaultAuthContext = {
    auth: defaultAuthContextData,
    setAuth: auth => {},
}

const authContext = createContext(defaultAuthContext)
export const useAuthContext = () => useContext(authContext)


export const AuthProvider = ({ children }) => {
    const [authData, setAuthData] = useState(defaultAuthContextData)
    const authContext_ = {
        auth: authData,
        setAuth: auth => {
            setAuthData(auth)
            localStorage.setItem('role', auth.role)
            localStorage.setItem('userId', auth.userId)
        },
    }
    return (
        <authContext.Provider value={authContext_}>
            { children }
        </authContext.Provider>
    )
}


export const AuthRequired = ({ checker, redirect, children }) => {
    const navigate = useNavigate()
    const { auth } = useAuthContext()

    useEffect(() => {
        if (!checker(auth)) {
            navigate(redirect)
        }
    }, [auth])


    return children
}

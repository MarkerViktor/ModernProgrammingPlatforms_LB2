import { Route, Routes } from 'react-router-dom'

import { AuthProvider, AuthRequired, Role, useAuthContext } from './Components/Main/Auth'
import { MainPage } from './Components/Pages/MainPage'
import { AdminPage } from './Components/Pages/AdminPage'
import { AboutPage } from './Components/Pages/AboutPage'
import { ContactsPage } from './Components/Pages/ContactsPage'
import { SignInPage } from './Components/Pages/SignInPage'
import { SignUpPage } from './Components/Pages/SignUpPage'


export const App = () => {
    return (
        <AuthProvider >
            <Routes>
                <Route path="/" element={
                    <AuthRequired checker={auth => [Role.ADMIN, Role.USER].includes(auth.role)} redirect='/sign-in'>
                        <MainPage />
                    </AuthRequired>
                } />
                <Route path="/admin" element={
                    <AuthRequired checker={auth => auth.role === Role.ADMIN} redirect='/'>
                        <AdminPage />
                    </AuthRequired>
                } />
                <Route path="/about" element={<AboutPage />} />
                <Route path="/contacts" element={<ContactsPage />} />
                <Route path="/sign-in" element={
                    <AuthRequired checker={auth => auth.role === Role.GUEST} redirect='/'>
                        <SignInPage />
                    </AuthRequired>
                } />
                <Route path="/sign-up" element={
                    <AuthRequired checker={auth => auth.role === Role.GUEST} redirect='/'>
                        <SignUpPage />
                    </AuthRequired>
                } />
            </Routes>
        </AuthProvider>
    )
}
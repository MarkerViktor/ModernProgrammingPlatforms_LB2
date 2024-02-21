import { Page } from '../Main/Page'
import { useState } from 'react'
import { useBackendClient } from '../../backend-client'
import { useAuthContext } from '../Main/Auth'


export const SignUpPage = () => {
    const { setAuth } = useAuthContext()
    const client = useBackendClient()

    const [firstName, setFirstName] = useState("")
    const [lastName, setLastName] = useState("")
    const [login, setLogin] = useState("")
    const [password, setPassword] = useState("")

    const onSubmit = async event => {
        if (!firstName || !lastName || !login || !password) {
            alert("Необходимо заполнить все поля формы!")
            return
        }

        try {
            await client.signUp(firstName, lastName, login, password)
        } catch (e) {
            alert('Ошибка регистрации. Введённый логин уже занят!')
            setLogin("")
            setPassword("")
            return
        }
        const auth = await client.signIn(login, password)
        localStorage.setItem('role', auth.role)
        localStorage.setItem('userId', auth.user_id)
        setAuth({
            role: auth.role,
            userId: auth.user_id,
        })
    }

    return (
        <Page name='Регистрация'>
            <form className="auth-login-form">
                <label htmlFor="firstName">Имя:</label>
                <input id="firstName" type="text" className="auth-text-input"
                       onChange={event => setFirstName(event.target.value)} value={firstName} />
                <label htmlFor="lastName">Фамилия:</label>
                <input id="lastName" type="text" className="auth-text-input"
                       onChange={event => setLastName(event.target.value)} value={lastName} />
                <label htmlFor="email">Логин:</label>
                <input id="email" type="email" className="auth-text-input"
                       onChange={event => setLogin(event.target.value)} value={login} />
                <label htmlFor="password">Пароль:</label>
                <input id="password" type="password" className="auth-text-input"
                       onChange={event => setPassword(event.target.value)} value={password} />
                <input type="button" value="Продолжить" onClick={onSubmit} className='auth-button' />
            </form>
        </Page>
    )
}

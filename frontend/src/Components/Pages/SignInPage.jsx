import { Page } from '../Main/Page'
import { useState } from 'react'
import { useBackendClient } from '../../backend-client'
import { useAuthContext } from '../Main/Auth'



export const SignInPage = () => {
    const { setAuth } = useAuthContext()
    const client = useBackendClient()

    const [login, setLogin] = useState("")
    const [password, setPassword] = useState("")

    const onSubmit = async event => {
        try {
            const auth = await client.signIn(login, password)
            localStorage.setItem('role', auth.role)
            localStorage.setItem('userId', auth.user_id)
            setAuth({
                role: auth.role,
                userId: auth.user_id,
            })
        } catch (e) {
            alert('Ошибка входа. Возможно введены неверные логин или пароль.')
            setPassword("")
        }
    }

    return (
        <Page name='Войти'>
            <form className="auth-login-form">
                <label htmlFor="email">Логин:</label>
                <input id="email" type="text" name="first_name" className="auth-text-input"
                       onChange={event => setLogin(event.target.value)} value={login} />
                <label htmlFor="password">Пароль:</label>
                <input id="password" type="password" name="last_name" className="auth-text-input"
                       onChange={event => setPassword(event.target.value)} value={password} />
                <input type="button" value="Войти" onClick={onSubmit} className='auth-button' />
            </form>
        </Page>
    )
}
import { useNavigate } from 'react-router-dom'
import { Role, useAuthContext } from '../Auth'
import { useBackendClient } from '../../../backend-client'


export const AuthAction = ({text, onClick}) => (
    <button onClick={onClick} className="auth-action">
        {text}
    </button>
)

export const AuthInfo = () => {
    const navigate = useNavigate()
    const { auth, setAuth } = useAuthContext()
    const client = useBackendClient()

    return (
        <div className='auth-layout'>
            {auth.role !== Role.GUEST ?
                <>
                    <AuthAction text='Выйти' onClick={
                        async _ => {
                            setAuth({role: Role.GUEST, userId: null})
                            await client.signOut()
                        }
                    } />
                </>: <>
                    <AuthAction text='Войти' onClick={ _ => navigate('/sign-in') } />
                    <AuthAction text='Регистрация' onClick={ _ => navigate('/sign-up') } />
                </>
            }
        </div>
    )
}

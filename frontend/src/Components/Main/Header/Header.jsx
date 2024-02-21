import { useNavigate } from 'react-router-dom'

import { Config } from '../../../config'
import { Role, useAuthContext } from '../Auth'

import { PageTitle } from './PageTitle'
import { Menu } from './Menu'
import { AuthInfo } from './AuthInfo'


export const Header = ({ title }) => {
    const { auth } = useAuthContext()
    const navigate = useNavigate()

    let menuItems = [
        {
            name: 'О сайте',
            onClick: () => navigate('/about')
        },
        {
            name: 'Контакты',
            onClick: () => navigate('/contacts')
        },
    ]

    if (auth.role === Role.ADMIN) {
        const adminPanelItem = {
            name: 'Панель администратора',
            onClick: () => navigate('/admin')
        }
        menuItems = [...menuItems, adminPanelItem]
    }

    return (
        <header>
            <div className="header-layout">
                <PageTitle title={Config.siteName} subTitle={title}/>
                <Menu items={menuItems}/>
                <AuthInfo auth={auth}/>
            </div>
        </header>
    )
}

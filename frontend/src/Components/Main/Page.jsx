import { Header } from './Header/Header'
import { Footer } from './Footer'


export const Page = ({name, children}) => {
    document.title = name
    return (<>
        <Header title={name}/>
        <div className="page">
            <div className="page-layout">
                {children}
            </div>
        </div>
        <Footer/>
    </>)
}

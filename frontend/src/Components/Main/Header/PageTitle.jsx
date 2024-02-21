import { Link } from 'react-router-dom'


export const PageTitle = ({title, subTitle}) => (
    <div className="title-layout">
        <Link to="/" className="link">
            <h1 className="title">
                { title }
            </h1>
        </Link>
        <div className="subtitle">
            { subTitle }
        </div>
    </div>
)


export const Menu = ({items}) => {
    const makeItem = ({name, onClick}) => (
        <button onClick={onClick} className='menu-item' key={name}>
            {name}
        </button>
    )
    return (
        <div className='menu'>
            { items.map(makeItem) }
        </div>
    )
}
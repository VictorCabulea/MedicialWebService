import bcrypt
from fastapi import APIRouter, Response, HTTPException, status, Query
from DTO.validationDTO import *
from Databases.SQL.SQLDatabase import Accounts
from DTO.accountDTO import AccountDTO

router = APIRouter()


def create_response_data(account: AccountDTO):
    response_data = {
        "account": {
            "id": account.id,
            "last_name": account.last_name,
            "first_name": account.first_name,
            "user_name": account.user_name,
            "user_email": account.user_email,
            "links": {
                "self": {
                    "href": f"/api/medicineProject/accounts/{account.id}", "type": "GET"
                },
                "update_last_name": {"href": f"/api/medicineProject/accounts/{account.id}/last_name", "type": "PUT"},
                "update_first_name": {"href": f"/api/medicineProject/accounts/{account.id}/first_name", "type": "PUT"},
                "update_user_name": {"href": f"/api/medicineProject/accounts/{account.id}/user_name", "type": "PUT"},
                "update_user_email": {"href": f"/api/medicineProject/accounts/{account.id}/user_email", "type": "PUT"},
                "update_password": {"href": f"/api/medicineProject/accounts/{account.id}/password", "type": "PUT"},
                "delete account": {
                    "href": f"/api/medicineProject/accounts/{account.id}", "type": "DELETE"
                }
            }
        },
    }

    return response_data


@router.post("/api/medicineProject/accounts")
async def create_account(
        account: AccountDTO,
        response: Response,
):
    existing_account_email = Accounts.get_or_none(user_email=account.user_email)

    if existing_account_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="An account with this email already exists")

    if is_valid_account(account):
        hashed_password = bcrypt.hashpw(account.password.encode("utf-8"), bcrypt.gensalt(rounds=15))
        new_account = Accounts.create(
            last_name=account.last_name,
            first_name=account.first_name,
            user_name=account.user_name,
            user_email=account.user_email,
            password=hashed_password
        )
        if bcrypt.checkpw(account.password.encode("utf-8"), hashed_password):
            print("Password is correct")
        else:
            print("Password is incorrect")

        response.status_code = status.HTTP_201_CREATED

        response_data = create_response_data(new_account)
    else:
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        response_data = {
            "message": "The account could not be registered due to errors in the input data!",
            "_links": {
                "view accounts": {"href": "/api/medicineProject/accounts", "type": "GET"},
                "add new account": {"href": "/api/medicineProject/accounts/create", "type": "POST"},
            }
        }

    return response_data


@router.get("/api/medicineProject/accounts/{account_id}")
async def get_account(account_id: int, response: Response):
    try:
        account = Accounts.get_by_id(account_id)

        response.status_code = status.HTTP_200_OK

        response_data = create_response_data(account)

        return response_data

    except Accounts.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )


@router.get("/api/medicineProject/accounts/")
async def get_accounts(
        response: Response,
        last_name: str = Query(None, title="Last Name", description="Last name of the account."),
        first_name: str = Query(None, title="First Name", description="First name of the account."),
        user_name: str = Query(None, title="User Name", description="User name of the account."),
        user_email: str = Query(None, title="User Email", description="User email of the account."),
):
    try:
        if last_name and first_name:
            if not (is_valid_name(last_name) and is_valid_name(first_name)):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Validation error in input data",
                )

            accounts = Accounts.filter((Accounts.last_name == last_name) & (Accounts.first_name == first_name))

        elif user_name:
            accounts = Accounts.filter(Accounts.user_name == user_name)

        elif user_email:
            if not is_valid_email(user_email):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Validation error in input data",
                )

            account = Accounts.get_by_user_email(user_email)
            response_data = create_response_data(account)
            return [response_data] if response_data else []

        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="At least one of last_name, first_name, user_name, or user_email should be provided.",
            )

        if not accounts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No accounts found with the given criteria.",
            )

        response.status_code = status.HTTP_200_OK
        response_data = [create_response_data(account) for account in accounts]
        return response_data

    except Accounts.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No accounts found with the given criteria.",
        )


@router.put("/api/medicineProject/accounts/{account_id}/last_name")
async def update_account_last_name(
        account_id: int,
        updated_last_name: str,
        response: Response,
):
    try:
        if is_valid_name(updated_last_name):
            account = Accounts.get_by_id(account_id)

            account.last_name = updated_last_name

            account.save()

            response.status_code = status.HTTP_204_NO_CONTENT
            return None
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Validation error in input data",
            )

    except Accounts.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )


@router.put("/api/medicineProject/accounts/{account_id}/first_name")
async def update_account_first_name(
        account_id: int,
        updated_first_name: str,
        response: Response,
):
    try:
        if is_valid_name(updated_first_name):
            account = Accounts.get_by_id(account_id)

            account.first_name = updated_first_name

            account.save()

            response.status_code = status.HTTP_204_NO_CONTENT
            return None
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Validation error in input data",
            )

    except Accounts.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )


@router.put("/api/medicineProject/accounts/{account_id}/user_name")
async def update_account_user_name(
        account_id: int,
        updated_user_name: str,
        response: Response,
):
    try:
        account = Accounts.get_by_id(account_id)

        account.user_name = updated_user_name

        account.save()

        response.status_code = status.HTTP_204_NO_CONTENT
        return None

    except Accounts.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )


@router.put("/api/medicineProject/accounts/{account_id}/user_email")
async def update_account_user_email(
        account_id: int,
        updated_user_email: str,
        response: Response,
):
    try:
        account = Accounts.get_by_id(account_id)
        conflicting_email_account = Accounts.get_or_none(user_email=updated_user_email)

        if conflicting_email_account:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Another account already has this email")
        else:
            if is_valid_email(updated_user_email):
                account.user_email = updated_user_email

                account.save()

                response.status_code = status.HTTP_204_NO_CONTENT
                return None
            else:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Validation error in input data",
                )

    except Accounts.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )


@router.put("/api/medicineProject/accounts/{account_id}/password")
async def update_account_password(
        account_id: int,
        current_password: str,
        new_password: str,
        response: Response,
):
    try:
        account = Accounts.get_by_id(account_id)

        if bcrypt.checkpw(current_password.encode("utf-8"), account.password.encode("utf-8")):
            print("Password is correct")
            if is_valid_password(new_password):
                account.password = new_password
                account.save()

                response.status_code = status.HTTP_204_NO_CONTENT
                return None
            else:
                raise HTTPException(
                    status_code=status.HTTP_200_OK,
                    detail="New password is too weak",
                )
        else:
            print("Password is incorrect")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect",
            )

    except Accounts.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )


@router.delete("/api/medicineProject/accounts/{account_id}")
async def delete_account(account_id: int, response: Response):
    try:
        account = Accounts.get_by_id(account_id)

        account.delete_instance()

        response.status_code = status.HTTP_204_NO_CONTENT

    except Accounts.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )

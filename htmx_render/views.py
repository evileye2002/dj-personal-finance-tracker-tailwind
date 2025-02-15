from django.http import HttpResponse
from django.shortcuts import render, resolve_url
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from account.forms import SignInForm, SignUpForm, UpdateUserInfoForm
from account.models import UpdateBalanceOperationType
from core.forms import TransactionForm, CategoryForm, GoalForm
from core.models import Transaction, TransactionType, Category, Goal, GoalPriority
from core.filter import TransactionFilter


# Create your views here.
def add_category(request):
    form = None
    categories = None
    message = None

    if request.method == "POST":
        form = CategoryForm(request.POST)

        if form.is_valid():
            new_category = form.save(commit=False)
            new_category.user = request.user
            new_category.save()

            form = None
            categories = Category.objects.filter(user=request.user)
            message = {"type": "alert-success", "value": "Thêm hạng mục thành công."}
        else:
            categories = Category.objects.filter(user=request.user)
            message = {"type": "alert-error", "value": "Thêm hạng mục thất bại."}

    ctx = {
        "form": form,
        "categories": categories,
        "message": message,
        "type": "add",
    }

    response = render(request, "component/category/category-update.html", ctx)
    if "success" in message["type"]:
        response["HX-TRIGGER"] = "addCategorySuccessfully"

    return response


def category_deltail(request, id):
    category = Category.objects.get(id=id, user=request.user)
    categories = Category.objects.filter(user=request.user)
    form = CategoryForm(instance=category)

    ctx = {
        "form": form,
        "categories": categories,
        "category": category,
    }
    return render(request, "partial/category/detail-category-form.html", ctx)


def update_category(request, id):
    category = Category.objects.get(id=id, user=request.user)
    form = CategoryForm(instance=category)
    message = None
    categories = None

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)

        if form.is_valid():
            form.save()

            form = None
            categories = Category.objects.filter(user=request.user)
            message = {
                "type": "alert-success",
                "value": "Cập nhật Hạng mục thành công.",
            }
        else:
            categories = Category.objects.filter(user=request.user)
            message = {"type": "alert-error", "value": "Cập nhật Hạng mục thất bại."}

    ctx = {
        "form": form,
        "categories": categories,
        "category": category,
        "message": message,
        "type": "edit",
    }

    response = render(request, "component/category/category-update.html", ctx)
    if "success" in message["type"]:
        response["HX-TRIGGER"] = "updateCategorySuccessfully"

    return response


def delete_category(request, id):
    categories = Category.objects.filter(user=request.user)
    message = None

    try:
        category = Category.objects.get(id=id, user=request.user)
        category.delete()
        message = {"type": "alert-success", "value": "Xoá Hạng mục thành công."}
    except Exception as ex:
        print(ex)
        message = {"type": "alert-error", "value": "Đã xảy ra lỗi khi xoá Hạng mục."}

    ctx = {
        "categories": categories,
        "message": message,
        "type": "delete",
    }
    response = render(request, "component/category/category-update.html", ctx)
    if "success" in message["type"]:
        response["HX-TRIGGER"] = "deleteCategorySuccessfully"
    return response


def category_option(request):
    categories = Category.objects.filter(
        user=request.user, type=TransactionType.EXPENSE
    )

    if request.method == "POST":
        post_data = request.POST.copy()
        type = (
            TransactionType.INCOME
            if post_data.get("is-income", "off") == "on"
            else TransactionType.EXPENSE
        )
        categories = Category.objects.filter(user=request.user, type=type)

    ctx = {"categories": categories}
    return render(request, "component/transaction/category-select-options.html", ctx)


def add_goal(request):
    form = None
    goals = None
    message = None

    if request.method == "POST":
        post_data = request.POST.copy()
        post_data["target_amount"] = post_data.get("target_amount", "").replace(",", "")
        form = GoalForm(post_data)

        if form.is_valid():
            new_goal = form.save(commit=False)
            new_goal.user = request.user
            new_goal.save()

            form = None
            goals = Goal.objects.filter(user=request.user)
            message = {"type": "alert-success", "value": "Thêm mục tiêu thành công."}
        else:
            goals = Goal.objects.filter(user=request.user)
            message = {"type": "alert-error", "value": "Thêm mục tiêu thất bại."}

    ctx = {
        "form": form,
        "goals": goals,
        "message": message,
        "type": "add",
    }

    response = render(request, "component/goal/page-layout.html", ctx)
    if "success" in message["type"]:
        response["HX-TRIGGER"] = "addGoalSuccessfully"

    return response


def goal_deltail(request, id):
    goal = Goal.objects.get(id=id, user=request.user)
    form = GoalForm(instance=goal)

    ctx = {
        "form": form,
        "goal": goal,
        "type": "detail",
    }
    return render(request, "partial/goal/detail-form.html", ctx)


def update_goal(request, id):
    goal = Goal.objects.get(id=id, user=request.user)
    form = GoalForm(instance=goal)
    message = None
    goals = None

    if request.method == "POST":
        post_data = request.POST.copy()
        post_data["target_amount"] = post_data.get("target_amount", "").replace(",", "")

        form = GoalForm(post_data, instance=goal)

        if form.is_valid():
            form.save()

            form = None
            goals = Goal.objects.filter(user=request.user)
            message = {
                "type": "alert-success",
                "value": "Cập nhật mục tiêu thành công.",
            }
        else:
            goals = Goal.objects.filter(user=request.user)
            message = {"type": "alert-error", "value": "Cập nhật mục tiêu thất bại."}

    ctx = {
        "form": form,
        "goals": goals,
        "goal": goal,
        "message": message,
        "type": "edit",
    }

    response = render(request, "component/goal/page-layout.html", ctx)
    if "success" in message["type"]:
        response["HX-TRIGGER"] = "updateGoalSuccessfully"

    return response


def delete_goal(request, id):
    goals = Goal.objects.filter(user=request.user)
    message = None

    try:
        goal = Goal.objects.get(id=id, user=request.user)
        goal.delete()
        message = {"type": "alert-success", "value": "Xoá mục tiêu thành công."}
    except Exception as ex:
        print(ex)
        message = {"type": "alert-error", "value": "Đã xảy ra lỗi khi xoá mục tiêu."}

    ctx = {
        "goals": goals,
        "message": message,
        "type": "delete",
    }
    response = render(request, "component/goal/page-layout.html", ctx)
    if "success" in message["type"]:
        response["HX-TRIGGER"] = "deleteGoalSuccessfully"

    return response


def add_transaction(request):
    form = None
    transactions = None
    message = None
    goals_incomplete = None
    categories = Category.objects.filter(user=request.user)

    if request.method == "POST":
        post_data = request.POST.copy()
        post_data["amount"] = post_data["amount"].replace(",", "")
        post_data["type"] = (
            TransactionType.INCOME
            if post_data.get("is-income", "off") == "on"
            else TransactionType.EXPENSE
        )

        form = TransactionForm(post_data)
        goals_incomplete = Goal.objects.filter(
            user=request.user,
            priority=GoalPriority.HIGH,
            target_amount__gt=request.user.balance,
        )
        categories = Category.objects.filter(user=request.user, type=post_data["type"])

        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            request.user.update_balance(
                transaction.amount,
                (
                    UpdateBalanceOperationType.ADD
                    if transaction.type == TransactionType.INCOME
                    else UpdateBalanceOperationType.SUBTRACT
                ),
            )

            message = {"type": "alert-success", "value": "Thêm giao dịch thành công."}
            transactions = Transaction.objects.filter(user=request.user)
        else:
            transactions = Transaction.objects.filter(user=request.user)
            message = {"type": "alert-error", "value": "Thêm giao dịch thất bại."}

    ctx = {
        "form": form,
        "goals_incomplete": goals_incomplete,
        "categories": categories,
        "transactions": transactions,
        "message": message,
        "type": "add",
    }

    response = render(request, "component/transaction/transaction-update.html", ctx)

    if "success" in message["type"]:
        response["HX-TRIGGER"] = "addTransactionSuccessfully"

    return response


def transaction_deltail(request, id):
    transaction = Transaction.objects.get(
        id=id, category__in=Category.objects.filter(user=request.user)
    )
    categories = Category.objects.filter(user=request.user, type=transaction.type)
    form = TransactionForm(instance=transaction)

    ctx = {
        "form": form,
        "categories": categories,
        "transaction": transaction,
        "type": "detail",
    }
    return render(request, "partial/transaction/detail-transaction-form.html", ctx)


def update_transaction(request, id):
    transaction = Transaction.objects.get(
        id=id,
        category__in=Category.objects.filter(user=request.user),
    )
    goals_incomplete = None
    categories = Category.objects.filter(user=request.user, type=transaction.type)
    form = TransactionForm(instance=transaction)
    message = None
    transactions = None
    old_amount = transaction.amount
    old_type = transaction.type

    if request.method == "POST":
        post_data = request.POST.copy()
        post_data["amount"] = post_data.get("amount", "").replace(",", "")
        post_data["type"] = (
            TransactionType.INCOME
            if post_data.get("is-income", "off") == "on"
            else TransactionType.EXPENSE
        )

        form = TransactionForm(post_data, instance=transaction)
        categories = Category.objects.filter(user=request.user, type=post_data["type"])

        if form.is_valid():
            new_transaction = form.save()

            request.user.update_balance(
                old_amount,
                (
                    UpdateBalanceOperationType.SUBTRACT
                    if old_type == TransactionType.INCOME
                    else UpdateBalanceOperationType.ADD
                ),
            )
            request.user.update_balance(
                new_transaction.amount,
                (
                    UpdateBalanceOperationType.ADD
                    if new_transaction.type == TransactionType.INCOME
                    else UpdateBalanceOperationType.SUBTRACT
                ),
            )

            form = None
            goals_incomplete = Goal.objects.filter(
                user=request.user,
                priority=GoalPriority.HIGH,
                target_amount__gt=request.user.balance,
            )
            transactions = Transaction.objects.filter(user=request.user)
            message = {
                "type": "alert-success",
                "value": "Cập nhật Giao dịch thành công.",
            }
        else:
            transactions = Transaction.objects.filter(user=request.user)
            message = {"type": "alert-error", "value": "Cập nhật Giao dịch thất bại."}

    ctx = {
        "form": form,
        "goals_incomplete": goals_incomplete,
        "categories": categories,
        "transactions": transactions,
        "transaction": transaction,
        "message": message,
        "type": "edit",
    }

    response = render(request, "component/transaction/transaction-update.html", ctx)
    if "success" in message["type"]:
        response["HX-TRIGGER"] = "updateTransactionSuccessfully"

    return response


def delete_transaction(request, id):
    transactions = Transaction.objects.filter(user=request.user)
    goals_incomplete = None
    message = None

    try:
        transaction = Transaction.objects.get(id=id, user=request.user)
        transaction.delete()
        request.user.update_balance(
            transaction.amount,
            (
                UpdateBalanceOperationType.SUBTRACT
                if transaction.type == TransactionType.INCOME
                else UpdateBalanceOperationType.ADD
            ),
        )
        goals_incomplete = Goal.objects.filter(
            user=request.user,
            priority=GoalPriority.HIGH,
            target_amount__gt=request.user.balance,
        )

        message = {"type": "alert-success", "value": "Xoá Giao dịch thành công."}
    except Exception as ex:
        print(ex)
        message = {"type": "alert-error", "value": "Đã xảy ra lỗi khi xoá giao dịch."}

    ctx = {
        "transactions": transactions,
        "goals_incomplete": goals_incomplete,
        "message": message,
        "type": "delete",
    }
    response = render(request, "component/transaction/transaction-update.html", ctx)
    if "success" in message["type"]:
        response["HX-TRIGGER"] = "deleteTransactionSuccessfully"

    return response


def filter_transaction(request):
    transaction_filter = TransactionFilter(
        request.GET,
        request=request,
        queryset=Transaction.objects.filter(user=request.user),
    )

    ctx = {
        "type": "filter",
        "filter": transaction_filter,
    }

    return render(request, "component/transaction/transaction-update.html", ctx)


def filter_category(request):
    categories = Category.objects.filter(user=request.user)
    search_str = request.GET.get("s", "")

    if search_str:
        categories = Category.objects.filter(
            user=request.user,
            name__icontains=search_str,
        )

    ctx = {
        "type": "search",
        "search_str": search_str,
        "categories": categories,
    }

    return render(request, "component/category/category-update.html", ctx)


def sign_in(request):
    form = SignInForm()
    next_url = request.GET.get("next")
    remember = None

    if request.method == "POST":
        form = SignInForm(request, data=request.POST)
        remember = request.POST.get("remember", "off")

        if form.is_valid():
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if remember == "on":
                    request.session.set_expiry(60 * 60 * 24 * 30 * 12)  # 1 year
                else:
                    request.session.set_expiry(60 * 60 * 24 * 7)  # 7 days

                login(request, user)
                redirect_url = next_url or resolve_url("home")
                response = HttpResponse()
                response["HX-Redirect"] = redirect_url
                return response

    field_errors = {
        field: error for field, error in form.errors.items() if field != "__all__"
    }
    non_field_errors = form.non_field_errors()
    ctx = {
        "form": form,
        "remember_value": remember,
        "field_errors": field_errors,
        "non_field_errors": non_field_errors,
    }

    return render(request, "partial/account/sign-in-form.html", ctx)


def sign_up(request):
    form = SignUpForm()

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            response = HttpResponse()
            response["HX-Redirect"] = resolve_url("sign-in")
            return response

    field_errors = {
        field: error for field, error in form.errors.items() if field != "__all__"
    }
    non_field_errors = form.non_field_errors()
    ctx = {
        "form": form,
        "field_errors": field_errors,
        "non_field_errors": non_field_errors,
    }

    return render(request, "partial/account/sign-up-form.html", ctx)


def update_user_info(request):
    form = UpdateUserInfoForm(instance=request.user)
    message = None

    if request.method == "POST":
        form = UpdateUserInfoForm(request.POST, request.FILES, instance=request.user)
        try:
            if form.is_valid():
                form.save()
                message = {
                    "type": "alert-success",
                    "value": "Thay đổi thông tin thành công.",
                }
            else:
                message = {
                    "type": "alert-error",
                    "value": "Thay đổi thông tin thất bại.",
                }
        except Exception as ex:
            message = {
                "type": "alert-error",
                "value": "Thay đổi thông tin thất bại.",
            }

    ctx = {
        "form": form,
        "message": message,
    }
    return render(request, "partial/account/update-user-info-form.html", ctx)


def change_password(request):
    form = PasswordChangeForm(request.user)
    message = None

    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        try:
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)

                form = None
                message = {
                    "type": "alert-success",
                    "value": "Đổi mật khhẩu thành công.",
                }
            else:
                message = {
                    "type": "alert-error",
                    "value": "Đổi mật khhẩu thất bại.",
                }
        except Exception as ex:
            message = {
                "type": "alert-error",
                "value": "Đổi mật khhẩu thất bại.",
            }

    ctx = {
        "form": form,
        "message": message,
    }
    response = render(request, "partial/account/change-password-form.html", ctx)
    if "success" in message["type"]:
        response["HX-TRIGGER"] = "changePasswordSuccessfully"
    return response
